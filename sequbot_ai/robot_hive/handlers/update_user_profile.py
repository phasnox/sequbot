from sequbot_data import shell_models as sm
from sequbot_data.shell_models.network import messages
from .base_handler import BaseHandler


class UpdateUserProfile(BaseHandler):

    @staticmethod
    def handle(bots, request):
        bot = BaseHandler.get_bot(bots, request.social_account_id)

        user_profile = bot.update_user_profile()

        # Build response
        response = messages.UpdateUserProfile.Response()
        response.user_profile = user_profile
        response.iguser_id    = bot.social_account.instagram_user.id

        return response
