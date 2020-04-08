import json


class Vector(list):
    def __init__(self, list_obj):
        super(Vector, self).__init__()
        self.extend(list_obj)

    def dumps(self):
        return json.dumps(self)

    def loads(self, raw_data):
        self[:] = []
        self.extend( json.loads(raw_data) )
        return self
