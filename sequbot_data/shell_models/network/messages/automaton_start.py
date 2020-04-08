from sequbot_data.shell_models.core import BaseModel, Field, ModelField


class TrainingOptions(BaseModel):
    models          = Field()
    rebuild_vectors = Field()

class AutomatonStart:
    class Request(BaseModel):
        fetch_followers  = Field()
        fetch_follows    = Field()
        training_options = ModelField(TrainingOptions)
        follow_followers = Field()
        follow_follows   = Field()
        ignore_cursor    = Field()

    class Response(BaseModel):
        automaton_state = Field()
        pid             = Field()
        host            = Field()
        error_msg       = Field()
