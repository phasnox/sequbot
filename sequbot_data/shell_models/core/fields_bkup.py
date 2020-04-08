

class Field:
    def __init__(self, name=None):
        self.name = name

    def getter(self, obj):
        return obj.get(self.name)
    
    def setter(self, obj, value):
        obj[self.name] = value


class Nested(Field):
    SEPARATOR = '.'
    def __init__(self, name):
        self.fields = name.split(Nested.SEPARATOR)
        super(Nested, self).__init__(name)

    def getter(self, obj):
        rvalue = obj
        try:
            for field in self.fields:
                rvalue = rvalue.get(field)
        except AttributeError:
            rvalue = None
        return rvalue
    
    def setter(self, obj, value):
        child = obj
        parent= None
        try:
            for field in self.fields:
                parent= child
                child = child[field]
            if isinstance(parent, dict): parent[filed] = value
        except AttributeError:
            pass


class Array(Nested):
    def __init__(self, clazz, field):
        self.saved_array = None
        self.clazz       = clazz
        super(Array, self).__init__(field)

    def getter(self, obj):
        if self.saved_array: return self.saved_array
        raw_array = super(Array, self).getter(obj)
        if raw_array:
            self.saved_array = [self.clazz(raw_object=el) for el in raw_array]
        else:
            self.saved_array = []
        return self.saved_array

    def setter(self, obj, value):
        self.saved_array = value
        raw_array        = [el.raw_object for el in value]
        super(Array, self).setter(obj, raw_array)


class ModelField(Field):
    def __init__(self, clazz, name=None):
        self.model_instance = None
        self.clazz          = clazz
        super(ModelField, self).__init__(name)

    def getter(self, obj):
        if not self.model_instance:
            raw_object = super(ModelField, self).getter(obj)
            self.model_instance = self.clazz(raw_object=raw_object)
        return self.model_instance

    def setter(self, obj, value):
        self.model_instance = value
        super(ModelField, self).setter(obj, value.raw_object)
