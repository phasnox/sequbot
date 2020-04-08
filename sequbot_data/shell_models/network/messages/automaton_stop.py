from sequbot_data.shell_models.core import BaseModel, Field


class AutomatonStop:
    class Request(BaseModel):
        delete_bot = Field()

    class Response(BaseModel):
        stopped   = Field()
        error_msg = Field()
