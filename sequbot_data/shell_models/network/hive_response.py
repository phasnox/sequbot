from sequbot_data.shell_models.core import BaseModel, Field, ModelField


class HiveResponse(BaseModel):
    class ErrorMessage(BaseModel):
        message    = Field()
        error_type = Field()

    uuid              = Field()
    social_account_id = Field()
    message           = Field()
    error             = ModelField(ErrorMessage)

    @staticmethod
    def response_from_error(error):
        response  = HiveResponse()
        error_msg = HiveResponse.ErrorMessage()

        error_msg.message    = str(error)
        error_msg.error_type = error.__class__.__name__

        response.error = error_msg
        return response
