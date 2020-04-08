from sequbot_data import shell_models as sm
from .base_handler import BaseHandler
from sequbot_data.shell_models.network import messages
from sequbot_data import models
from robot_hive.errors import RobotBusy
from robot.automata.errors import AutomataError


class InstagramAuthenticate(BaseHandler):

    @staticmethod
    def handle(bots, request):
        # Parse request message
        parsed_request = messages.InstagramAuthenticate.Request(raw_data=request.message)

        # On bot creation, it tries to authenticat
        try:
            bot = BaseHandler.get_bot(bots, request.social_account_id)
            # Authenticate
            bot.authenticate(parsed_request.username, parsed_request.password)
        except AutomataError:
            sa = models.SocialAccount.objects.get(pk=request.social_account_id)
            sa.username = parsed_request.username
            sa.set_password(parsed_request.password)
            sa.save(update_fields=['username', 'password'])
            bot = BaseHandler.get_bot(bots, request.social_account_id)

        # Verify nothing is running
        if bot.cycle and bot.cycle.is_alive():
            raise RobotBusy('Bot for {} is in state: {}'.format(bot.username, bot.state))

        user_profile = bot.fetch_user(parsed_request.username)

        # Build response
        response = messages.InstagramAuthenticate.Response()
        response.user_profile = user_profile
        return response
