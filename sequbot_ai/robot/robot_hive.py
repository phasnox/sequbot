from multiprocessing.managers import BaseManager

class RobotManager(BaseManager):
    pass

def start():
    manager = BaseManager(address=('', 7777), authkey=b'210913')
    server = manager.get_server()
    server.serve_forever()
