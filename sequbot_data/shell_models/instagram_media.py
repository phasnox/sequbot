from .core import BaseModel, Nested, Field


class InstagramMedia(BaseModel):
    caption        = Field()
    code           = Field()
    comments_count = Nested('comments.count')
    date           = Field()
    ig_id          = Field('id')
    is_video       = Field()
    likes_count    = Nested('likes.count')
    display_src    = Field()
    thumbsnail_src = Field()
    height         = Nested('dimensions.height')
    width          = Nested('dimensions.width')
