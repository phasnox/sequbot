from sequbot_data.shell_models.core import BaseModel, Field, ModelField
from sequbot_data.shell_models import InstagramUserProfile


class AddFollowSource:
    class Request(BaseModel):
        username = Field()

    class Response(BaseModel):
        user_profile = ModelField(InstagramUserProfile)
