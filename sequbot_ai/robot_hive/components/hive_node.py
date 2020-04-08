from queue import Queue, Empty
import uuid
from twisted.internet import threads
from sequbot_data.shell_models.network import HiveResponse


class HiveNode():
    node_queues = {}
    def __init__(self, protocol):
        self.protocol = protocol
        self.load     = 0
        super(HiveNode, self).__init__()

    def get(self, request, timeout=None):
        if not request.uuid:
            request.uuid = str(uuid.uuid4())

        # Create queue
        queue = self.node_queues[request.uuid] = Queue()

        # Send request
        self.protocol.transport.write(request.dumps().encode())

        # Get request
        def get_from_queue():
            try:
                response = queue.get(timeout=timeout)
                del self.node_queues[request.uuid]
            except Empty:
                response = HiveResponse()
                error    = HiveResponse.ErrorMessage()
                error.message = 'Empty response from node'
                response.error = error
            return response

        d = threads.deferToThread(get_from_queue)
        return d

    def put(self, response):
        queue = self.node_queues[response.uuid]
        queue.put(response)
