from sequbot_data.shell_models.core import BaseModel, Field, ModelField
from sequbot_data.shell_models import InstagramUserProfile

class InstagramAuthenticate:
    class Request(BaseModel):
        username = Field()
        password = Field()

    class Response(BaseModel):
        user_profile = ModelField(InstagramUserProfile)
