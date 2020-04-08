from .core import BaseModel, Field


class AiConfig(BaseModel):
    '''
    This class holds user set conditions to determine who is a target to follow
    '''
    user_follows        = Field() # The 'user follows' target
    follows_user        = Field() # The target 'follows user'
    auto_follow_sources = Field() # The target 'follows user'

    def __bool__(self):
        return self.user_follows is not None or self.follows_user is not None
