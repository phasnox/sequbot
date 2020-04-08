

class Field:
    def __init__(self, name=None):
        self.name = name

    def getter(self, base_model):
        return base_model.raw_object.get(self.name)
    
    def setter(self, base_model, value):
        base_model.raw_object[self.name] = value


class Nested(Field):
    SEPARATOR = '.'
    def __init__(self, name):
        self.fields = name.split(Nested.SEPARATOR)
        super(Nested, self).__init__(name)

    def getter(self, base_model):
        rvalue = base_model.raw_object
        try:
            for field in self.fields:
                rvalue = rvalue.get(field)
        except AttributeError:
            rvalue = None
        return rvalue
    
    def setter(self, base_model, value):
        child = base_model.raw_object
        parent= None
        try:
            for field in self.fields:
                parent= child
                child = child.get(field)
            if isinstance(parent, dict): parent[filed] = value
        except AttributeError:
            pass


class ReadOnlyArray(Nested):
    def __init__(self, clazz, field):
        self.clazz       = clazz
        super(ReadOnlyArray, self).__init__(field)

    def getter(self, base_model):
        key   = '__' + self.name
        value = base_model.field_instances.get(key)
        if value is not None: return value

        raw_array = super(ReadOnlyArray, self).getter(base_model)
        if raw_array is not None:
            value = [self.clazz(raw_object=el) for el in raw_array]
            base_model.field_instances[key] = value
            return value
        else:
            return []

    def setter(self, obj, value):
        raise AttributeError('Field {} is read-only'.format(self.name))


class ModelField(Field):
    def __init__(self, clazz, name=None):
        self.clazz = clazz
        super(ModelField, self).__init__(name)

    def getter(self, base_model):
        key   = '__' + self.name
        value = base_model.field_instances.get(key)
        if value is not None: return value

        raw_object = super(ModelField, self).getter(base_model)
        if raw_object is not None:
            value = self.clazz(raw_object=raw_object)
            base_model.field_instances[key] = value
            return value

    def setter(self, base_model, value):
        if value and not isinstance(value, self.clazz):
            raise TypeError('Value must be of type {}'.format(self.clazz.__name__))
        key   = '__' + self.name
        base_model.field_instances[key] = value
        if value is not None:
            base_model.raw_object[self.name] = value.raw_object
