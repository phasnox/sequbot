from .core import BaseModel, Field, ModelField


class Params(BaseModel):
    weights        = Field()
    bias           = Field()
    word_features  = Field()

    def __bool__(self):
        return ((self.weights is not None and len(self.weights)>0) 
                and (self.bias is not None and len(self.bias)>0)
                and (self.word_features is not None and len(self.word_features)>0))


class AIParams(BaseModel):
    bio     = ModelField(Params)
    caption = ModelField(Params)

    def __init__(self, raw_data=None, raw_object=None):
        super(AIParams, self).__init__(raw_data, raw_object)

        if self.bio is None:
            self.bio = Params()

        if self.caption is None:
            self.caption = Params()

    def __bool__(self):
        return bool(self.bio) and bool(self.caption)
