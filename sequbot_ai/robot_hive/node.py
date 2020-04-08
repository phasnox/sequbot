import logging
import signal
from twisted.internet import protocol, reactor, endpoints
from twisted.internet import threads

# sequbot_data
from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import HiveRequest, HiveResponse
from sequbot_data.robot_hive import HIVE_PATHS
from sequbot_data.robot_hive.constants import HIVE_HANDSHAKE

# Robot imports
from robot_hive.errors import HiveUnkownPath, HiveConnectionError
from robot_hive import handlers
from robot import loggers

logger = logging.getLogger('robot_hive')

PATHS_HANDLERS = {
    HIVE_PATHS.INSTAGRAM_AUTHENTICATE: handlers.InstagramAuthenticate,
    HIVE_PATHS.FETCH_INSTAGRAM_USER:   handlers.FetchInstagramUser,
    HIVE_PATHS.AUTOMATON_CHECK:        handlers.AutomatonCheck,
    HIVE_PATHS.AUTOMATON_START:        handlers.AutomatonStart,
    HIVE_PATHS.AUTOMATON_STOP:         handlers.AutomatonStop,
    HIVE_PATHS.UPDATE_USER_PROFILE:    handlers.UpdateUserProfile,
    HIVE_PATHS.ADD_FOLLOW_SOURCE:      handlers.AddFollowSource,
}


class HIVE_NODE_STATES:
    READY      = 0
    CONNECTING = 1
    IDENTIFYING= 2
    ONLINE     = 3
    ERROR      = 4


class HiveNodeProtocol(protocol.Protocol):
    def __init__(self, hive_client_factory):
        self.factory = hive_client_factory
        self.state   = HIVE_NODE_STATES.READY
        super(HiveNodeProtocol, self).__init__()

    def connectionMade(self):
        logger.info('Connecting..')
        self.state = HIVE_NODE_STATES.CONNECTING

    def dataReceived(self, data):
        raw_data = data.decode()
        if self.handshake(raw_data): return

        # Parse request
        logger.info('Processing request..')
        request = HiveRequest(raw_data=raw_data)
        handler = PATHS_HANDLERS.get(request.path)

        def handle():
            try:
                if handler:
                    response_message = handler.handle(self.factory.bots, request)
                else:
                    raise HiveUnkownPath('Unknown path')

                response         = HiveResponse()
                response.uuid    = request.uuid
                response.message = response_message.dumps()
            except Exception as e:
                logger.exception(e)
                response         = HiveResponse.response_from_error(e)
                response.uuid    = request.uuid

            logger.info('Request processed..')
            return response.dumps().encode()

        d = threads.deferToThread(handle)
        d.addCallback(self.transport.write)

    def handshake(self, raw_data):
        if self.state == HIVE_NODE_STATES.CONNECTING:
            hive_cluster_id = HIVE_HANDSHAKE.get_hive_cluster_id(raw_data)
            logger.info('Identifying to hive cluster: {}'.format(hive_cluster_id))
            if hive_cluster_id:
                # Verify hive_cluster_id
                if hive_cluster_id != self.factory.hive_cluster_id:
                    logger.info('New hive cluster found. Cleaning up..'.format(hive_cluster_id))
                    if not self.factory.hive_cluster_id:
                        self.factory.stop_bots()
                    self.factory.hive_cluster_id = hive_cluster_id

                self.transport.write(HIVE_HANDSHAKE.NODE.encode())
                self.state = HIVE_NODE_STATES.IDENTIFYING
                return True
            else:
                raise HiveConnectionError('Error during handshake. Server response.')
        elif self.state == HIVE_NODE_STATES.IDENTIFYING:
            if raw_data == HIVE_HANDSHAKE.SUCCESS:
                logger.info('Online!')
                self.state = HIVE_NODE_STATES.ONLINE
                return True
            else:
                raise HiveConnectionError('Error during handshake. Server response.')


class HiveNodeFactory(protocol.ReconnectingClientFactory):
    hive_cluster_id = None
    bots            = {}
    maxRetries      = 3
    reconnect_count = 0
    def buildProtocol(self, addr):
        self.retry_count = 0
        self.resetDelay()
        return HiveNodeProtocol(self)

    def clientConnectionLost(self, connector, reason):
        logger.info('Lost connection.  Reason: {}'.format(reason))
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        self.reconnect_count += 1
        logger.info('Connection failed. Reason: {}. Reconnection retries: {}'.format(reason, self.reconnect_count))
        if self.reconnect_count == self.maxRetries:
            self.stop_bots()
            reactor.stop()
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def stop_bots(self):
        logger.info('Stopping all bots..')
        for social_account_id, bot in self.bots.items():
            bot.stop()
        self.bots = {}

    def __del__(self):
        self.stop_bots()

def start(host, port):
    loggers.add_handlers('node')
    logger.info('Start hive node..')
    factory = HiveNodeFactory()

    # Handle kill gracefully
    def handle_kill():
        logger.info('Stopping node gracefully')
        factory.stop_bots()

    # Connect to Server
    reactor.addSystemEventTrigger('before', 'shutdown', handle_kill)
    reactor.connectTCP(host, port, factory)
    reactor.run()

if __name__ == '__main__':
    # Setup the django app
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sequbot_ai.settings')
    import django
    django.setup()
    start()
