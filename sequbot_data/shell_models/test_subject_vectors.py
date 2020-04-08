from .core import BaseModel, Field


class TestSubjectVectors(BaseModel):
    bio     = Field()
    caption = Field()
