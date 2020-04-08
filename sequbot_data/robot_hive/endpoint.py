import socket
import select
from sequbot_data.shell_models.network import HiveResponse
from sequbot_data.robot_hive import constants
from .errors import HiveConnectionError, HiveEmptyResponse

BUFSIZE       = 1 
MSG_SEPARATOR = '\n'
HIVE_HOST     = constants.HIVE_MASTER_HOST
HIVE_PORT     = constants.HIVE_PORT
TIMEOUT       = 60

# Read all method to read from socket
def readall(sock, timeout=TIMEOUT):
    sock.setblocking(0)
    msg = []
    read_ready, _, _ = select.select([sock], [], [], timeout)
    if sock in read_ready:
        while True:
            try:
                chunk = sock.recv(BUFSIZE)
                if not chunk:
                    break
                msg.append(chunk.decode())
            except socket.error as e:
                if e.errno == 11 :
                    break
                raise e
    return ''.join(msg)


class HiveEndpoint:

    @staticmethod
    def send(request):
        if not request: return
        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HIVE_HOST, HIVE_PORT))
        s.setblocking(0)

        #Handshake
        handshake_init = readall(s)
        cluster_id     = constants.HIVE_HANDSHAKE.get_hive_cluster_id(handshake_init)
        if not cluster_id:
            raise HiveConnectionError('Error during handshake. Identifying')

        s.sendall(constants.HIVE_HANDSHAKE.CLIENT.encode())
        handshake_success = readall(s)

        if handshake_success != constants.HIVE_HANDSHAKE.SUCCESS:
            raise HiveConnectionError('Error during handshake. After identify')

        # Send message
        msg = request.dumps()
        s.sendall(msg.encode())

        # Receive and parse response
        data = readall(s)

        if not data:
            raise HiveEmptyResponse('Empty response from server')

        response = HiveResponse(raw_data=data)
        s.close()

        return response
