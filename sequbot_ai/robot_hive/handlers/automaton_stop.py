from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class AutomatonStop(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id, False)
        running = False

        if bot:
            parsed_request = messages.AutomatonStop.Request(raw_data=request.message)
            bot.stop()
            running = bot.cycle and bot.cycle.is_alive()
            pid     = bot.cycle and bot.cycle.pid

            # Remove cycle
            bot.cycle = None

            if parsed_request.delete_bot:
                del bot
                del bots[request.social_account_id]

        # Build response
        response         = messages.AutomatonStop.Response()
        response.stopped = not running
        if running:
            response.pid = pid

        return response
