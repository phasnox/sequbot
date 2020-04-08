from sequbot_data import shell_models as sm
from sequbot_data import models
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class AutomatonStart(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id)
        parsed_request = messages.AutomatonStart.Request(raw_data=request.message)

        if bot.cycle and bot.cycle.is_alive():
            # Build response
            response = messages.AutomatonStart.Response()
            response.automaton_state = bot.state
            response.error_msg       = 'Action already running: {}'.format(bot.state)
            return response

        bot.start(parsed_request.ignore_cursor, parsed_request.training_options)

        # Build response
        response = messages.AutomatonStart.Response()
        response.automaton_state = bot.state
        return response
