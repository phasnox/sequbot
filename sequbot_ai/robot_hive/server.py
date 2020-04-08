import logging
from twisted.internet import protocol, reactor, endpoints
from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import HiveRequest, HiveResponse
from sequbot_data.robot_hive import HIVE_PATHS
from sequbot_data.robot_hive.constants import HIVE_PORT, HIVE_HANDSHAKE
from sequbot_data.robot_hive.constants import HIVE_CLIENT_TIMEOUT
from robot import loggers
from robot_hive.components import HiveCluster

logger = logging.getLogger('robot_hive')

class HIVE_SERVER_STATES:
    READY      = 0
    CONNECTING = 1
    NODE       = 2
    CLIENT     = 3
    ERROR      = 4

CLIENT_TYPE_STATE = {
    HIVE_HANDSHAKE.NODE:   HIVE_SERVER_STATES.NODE,
    HIVE_HANDSHAKE.CLIENT: HIVE_SERVER_STATES.CLIENT,
}

class HiveServerProtocol(protocol.Protocol):
    def __init__(self, hive_cluster):
        self.hive_cluster = hive_cluster
        self.state = HIVE_SERVER_STATES.READY
        self.node  = None
        super(HiveServerProtocol, self).__init__()

    def connectionMade(self):
        self.state = HIVE_SERVER_STATES.CONNECTING
        init_msg   = '{}:{}'.format(HIVE_HANDSHAKE.INIT, self.hive_cluster.id)
        self.transport.write(init_msg.encode())

    def dataReceived(self, data):
        raw_data = data.decode()
        if self.state == HIVE_SERVER_STATES.ERROR:
            self.transport.write(HIVE_HANDSHAKE.ERROR.encode())
            return

        if self.state == HIVE_SERVER_STATES.CONNECTING:
            state = self.state = CLIENT_TYPE_STATE.get(raw_data)
            if state:
                if state == HIVE_SERVER_STATES.NODE:
                    logger.info('New node connected!')
                    self.node = self.hive_cluster.add_node(self)
                elif state == HIVE_SERVER_STATES.CLIENT:
                    logger.info('New client connected!')
                self.transport.write(HIVE_HANDSHAKE.SUCCESS.encode())
            else:
                self.transport.write(HIVE_HANDSHAKE.ERROR.encode())
            return

        if self.state == HIVE_SERVER_STATES.NODE:
            logger.info('Response from node received')
            response  = HiveResponse(raw_data=raw_data)
            try:
                node = self.hive_cluster.get_node(response.social_account_id)
            except Exception as e:
                response = HiveResponse.response_from_error(e)
            node.put(response)
            
        if self.state == HIVE_SERVER_STATES.CLIENT:
            logger.info('Request from client received')
            request  = HiveRequest(raw_data=raw_data)
            node     = self.hive_cluster.get_node(request.social_account_id)
            response = node.get(request, timeout=HIVE_CLIENT_TIMEOUT)
            response.addCallback(lambda r: self.transport.write(r.dumps().encode()))
            

    def connectionLost(self, reason):
        logger.info('Connection lost: {}'.format(reason))
        if self.state == HIVE_SERVER_STATES.NODE:
            logger.info('Removing node..')
            self.hive_cluster.remove_node(self.node)


class HiveServerFactory(protocol.Factory):
    hive_cluster = HiveCluster()
    def buildProtocol(self, addr):
        return HiveServerProtocol(self.hive_cluster)


def start(port):
    loggers.add_handlers('server')
    logger.info('Start robot hive server..')
    endpoints.TCP4ServerEndpoint(reactor, port).listen(HiveServerFactory())
    reactor.run()

if __name__ == '__main__':
    start()
