import queue


class Action:

    def __init__(self, cancel_request_queue = None):
        self.__cancel_queue = cancel_request_queue
        pass

    # Cancel requested
    @property
    def cancel_requested(self):
        if not self.__cancel_queue: return False
        try:
            return self.__cancel_queue.get(block=False)
        except queue.Empty: pass
