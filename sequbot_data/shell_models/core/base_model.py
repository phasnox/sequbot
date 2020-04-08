import json
from .fields import Field


class BaseModel(object):
    raw_object      = None
    field_instances = None
    def __init__(self, raw_data=None, raw_object=None):
        self.field_instances = {}
        if raw_data:
            BaseModel.loads(self, raw_data)
        elif raw_object is not None:
            self.raw_object = raw_object
        else:
            self.raw_object = {}

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if isinstance(attr, Field):
            attr.name = attr.name or name
            return attr.getter(self)
        else:
            return attr

    def __setattr__(self, name, value):
        attr = object.__getattribute__(self, name)
        if isinstance(attr, Field):
            attr.name = attr.name or name
            attr.setter(self, value)
        else:
            object.__setattr__(self, name, value)

    def dumps(self):
        return json.dumps(self.raw_object)

    def loads(self, raw_data):
        self.raw_object = json.loads(raw_data)
        return self
