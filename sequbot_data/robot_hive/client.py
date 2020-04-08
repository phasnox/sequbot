from sequbot_data.shell_models.network import HiveRequest
from sequbot_data.shell_models.network import messages
from .constants import HIVE_TEST_MODES
from .endpoint import HiveEndpoint
from .errors import HiveErrorInResponse
from .paths import HIVE_PATHS


class HiveClient:
    test_mode = HIVE_TEST_MODES.NONE

    @staticmethod
    def __send(path, social_account_id, message, test_mode):
        request = HiveRequest()
        request.social_account_id = social_account_id
        request.path              = path
        request.message           = message.dumps()
        request.test_mode         = test_mode
        response = HiveEndpoint.send(request)
        if response.error:
            raise HiveErrorInResponse(response.error.message, request, response)
        return response.message

    @staticmethod
    def instagram_authenticate(social_account_id, username, password, test_mode=HIVE_TEST_MODES.NONE):
        request          = messages.InstagramAuthenticate.Request()
        request.username = username
        request.password = password
        response = HiveClient.__send(
                HIVE_PATHS.INSTAGRAM_AUTHENTICATE, 
                social_account_id, request, test_mode)
        return messages.InstagramAuthenticate.Response(raw_data=response)

    @staticmethod
    def fetch_instagram_user(social_account_id, username, test_mode=HIVE_TEST_MODES.NONE):
        request          = messages.FetchInstagramUser.Request()
        request.username = username
        response = HiveClient.__send(
                HIVE_PATHS.FETCH_INSTAGRAM_USER, 
                social_account_id, request, test_mode)
        return messages.FetchInstagramUser.Response(raw_data=response)

    @staticmethod
    def automaton_start(social_account_id, request=messages.AutomatonStart.Request(), test_mode=HIVE_TEST_MODES.NONE):
        if not isinstance(request, messages.AutomatonStart.Request):
            raise TypeError('Parameter `request` must be of type AutomatonStart.Request')
        response = HiveClient.__send(
                HIVE_PATHS.AUTOMATON_START, 
                social_account_id, request, test_mode)
        return messages.AutomatonStart.Response(raw_data=response)

    @staticmethod
    def automaton_stop(social_account_id, delete_bot=False, test_mode=HIVE_TEST_MODES.NONE):
        request  = messages.AutomatonStop.Request()
        request.delete_bot = delete_bot
        response = HiveClient.__send(
                HIVE_PATHS.AUTOMATON_STOP, 
                social_account_id, request, test_mode)
        return messages.AutomatonStop.Response(raw_data=response)

    @staticmethod
    def automaton_check(social_account_id, test_mode=HIVE_TEST_MODES.NONE):
        request  = messages.AutomatonCheck.Request()
        response = HiveClient.__send(
                HIVE_PATHS.AUTOMATON_CHECK, 
                social_account_id, request, test_mode)
        return messages.AutomatonCheck.Response(raw_data=response)

    @staticmethod
    def update_user_profile(social_account_id, test_mode=HIVE_TEST_MODES.NONE):
        request  = messages.UpdateUserProfile.Request()
        response = HiveClient.__send(
                HIVE_PATHS.UPDATE_USER_PROFILE, 
                social_account_id, request, test_mode)
        return messages.UpdateUserProfile.Response(raw_data=response)

    @staticmethod
    def add_follow_source(social_account_id, username, test_mode=HIVE_TEST_MODES.NONE):
        request          = messages.AddFollowSource.Request()
        request.username = username
        response = HiveClient.__send(
                HIVE_PATHS.ADD_FOLLOW_SOURCE, 
                social_account_id, request, test_mode)
        return messages.FetchInstagramUser.Response(raw_data=response)
