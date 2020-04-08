from .core import BaseModel, Nested, ReadOnlyArray, Field
from .instagram_media import InstagramMedia


class InstagramUserProfile(BaseModel):
    biography             =  Field()
    media                 =  ReadOnlyArray(InstagramMedia, 'media.nodes')
    blocked_by_viewer     =  Field()
    followed_by_viewer    =  Field()
    external_url          =  Field()
    followed_by_count     =  Nested('followed_by.count')
    follows_count         =  Nested('follows.count')
    follows_viewer        =  Field()
    full_name             =  Field()
    has_blocked_viewer    =  Field()
    has_requested_viewer  =  Field()
    ig_id                 =  Field('id')
    is_private            =  Field()
    media_count           =  Nested('media.count')
    profile_pic_url       =  Field()
    requested_by_viewer   =  Field()
    username              =  Field()

    def __bool__(self):
        return self.ig_id is not None
