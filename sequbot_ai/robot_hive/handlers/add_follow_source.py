from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class AddFollowSource(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id)
        parsed_request = messages.AddFollowSource.Request(raw_data=request.message)

        # Build response
        response = messages.FetchInstagramUser.Response()
        fs = bot.add_follow_source(parsed_request.username)
        response.user_profile = sm.InstagramUserProfile(
                raw_data=fs.instagram_user.raw_data)

        return response
