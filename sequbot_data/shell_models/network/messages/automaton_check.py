from sequbot_data.shell_models.core import BaseModel, Field


class AutomatonCheck:
    class STATUS:
        ERROR   = 'ERROR'
        RUNNING = 'RUNNING'
        IDLE    = 'IDLE'

    class Request(BaseModel): pass

    class Response(BaseModel):
        status    = Field()
        action    = Field()
        error_msg = Field()
        error_type= Field()
