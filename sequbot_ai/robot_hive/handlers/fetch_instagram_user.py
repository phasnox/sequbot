from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class FetchInstagramUser(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id)

        parsed_request = messages.FetchInstagramUser.Request(raw_data=request.message)

        # Build response
        response = messages.FetchInstagramUser.Response()
        response.user_profile = bot.fetch_user(parsed_request.username)

        return response
