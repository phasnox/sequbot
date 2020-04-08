from .core import BaseModel, Field


class Features(BaseModel):
    bio     = Field()
    caption = Field()
