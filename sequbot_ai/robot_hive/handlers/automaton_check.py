from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class AutomatonCheck(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id)

        # Get status and error
        status = messages.AutomatonCheck.STATUS.IDLE
        error  = None
        if bot.cycle and bot.cycle.is_alive():
            status = messages.AutomatonCheck.STATUS.RUNNING

        if bot.cycle and bot.cycle.error:
            status = messages.AutomatonCheck.STATUS.ERROR
            error  = bot.cycle.error

        # Build response
        response = messages.AutomatonCheck.Response()
        response.status     = status
        if error:
            response.error_msg  = error.message
            response.error_type = error.__class__.__name__
        return response
