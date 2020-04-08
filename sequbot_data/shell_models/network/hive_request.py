from sequbot_data.shell_models.core import BaseModel, Field

class HiveRequest(BaseModel):
    uuid              = Field()
    social_account_id = Field()
    path              = Field()
    test_mode         = Field()
    message           = Field()
