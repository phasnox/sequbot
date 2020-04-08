from sequbot_data.shell_models.core import BaseModel, Field, ModelField
from sequbot_data import shell_models as sm


class UpdateUserProfile:
    class Request(BaseModel): pass

    class Response(BaseModel):
        user_profile = ModelField(sm.InstagramUserProfile)
        iguser_id    = Field()
