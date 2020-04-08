import json
import logging
from .http_interface import HttpInterface
from .variables import CORE_HEADERS
from .variables import INIT_URL
from .variables import AJAX_HEADERS
from .variables import LOGIN_URL
from .variables import FOLLOW_URL
from .variables import UNFOLLOW_URL
from .variables import PROFILE_URL
from .variables import INTEGRITY_CHECKPOINT_URL
from .paginated import Followers
from .paginated import Follows
from .errors import InstagramHackAPIError

logger = logging.getLogger('instagram_hack_api')

class InstagramHackAPI:
    def __init__(self, cookies=None):
        self.http     = HttpInterface(cookies=cookies)
        self.username = None

    @property
    def cookies(self):
        return self.http.cookies

    def authenticate(self, username, password):
        # First response to get csrftoken
        request_headers = CORE_HEADERS.copy()
        init_response   = self.http.get(INIT_URL, headers=request_headers)

        # Login
        login_data={'username': username, 'password': password}
        request_headers.update({
            'x-csrftoken': self.http.session.cookies.get('csrftoken'),
            'referer': 'https://www.instagram.com'
        })
        request_headers.update(AJAX_HEADERS)
        login_response = self.http.post(LOGIN_URL, data=login_data, headers=request_headers)
        if not self.http.cookies.get('sessionid'):
            raise InstagramHackAPIError('Unable to authenticate. Sessionid empty', response=login_response)
        self.username = username

    def integrity_checkpoint(self):
        csrftoken = self.http.session.cookies.get('csrftoken')
        form_data={'csrfmiddlewaretoken': csrftoken, 'approve': 'It Was Me'}
        request_headers = CORE_HEADERS.copy()
        request_headers.update({
            'x-csrftoken': csrftoken,
            'referer': 'https://www.instagram.com'
        })
        response = self.http.post(INTEGRITY_CHECKPOINT_URL, data=form_data, headers=request_headers)
        return response

    def unfollow(self, username, user_id):
        request_headers = CORE_HEADERS.copy()
        request_headers.update(AJAX_HEADERS)
        request_headers.update({
            'x-csrftoken': self.http.session.cookies.get('csrftoken'),
            'referer': 'https://www.instagram.com/{}/'.format(username)
        })
        unfollow_url = UNFOLLOW_URL.format(user_id)
        response     = self.http.post(unfollow_url, headers=request_headers)
        return json.loads(response.text)

    def follow(self, username, user_id):
        request_headers = CORE_HEADERS.copy()
        request_headers.update(AJAX_HEADERS)
        request_headers.update({
            'x-csrftoken': self.http.session.cookies.get('csrftoken'),
            'referer': 'https://www.instagram.com/{}/'.format(username)
        })
        follow_url = FOLLOW_URL.format(user_id)
        response   = self.http.post(follow_url, headers=request_headers)
        return json.loads(response.text)

    def followers(self, username=None, cursor=None):
        username = username or self.username
        if not username:
            raise InstagramHackAPIError('You must provide a username to fetch followers')
        return Followers(self.http, username, cursor=cursor)

    def follows(self, username=None, cursor=None):
        username = username or self.username
        if not username:
            raise InstagramHackAPIError('You must provide a username to fetch follows')
        return Follows(self.http, username, cursor=cursor)

    def user(self, username):
        request_headers = CORE_HEADERS.copy()
        request_headers.update(AJAX_HEADERS)
        response = self.http.get(PROFILE_URL.format(username), headers=request_headers)
        if not response.text:
            logger.error('Empty response trying to fetch user {}'.format(username))
            raise InstagramHackAPIError('Empty response')
        try:
            data = json.loads(response.text)
        except ValueError:
            logger.error('Error while parsing user {}'.format(username))
            raise InstagramHackAPIError('Error while parsing response',
                    response=response)
            # We got in here because we got a page not found and response.text
            # is html. This may be due to the user blocking our client's user
            # or the most general case, when intagram blocks the user for too
            # much following.
            #return None
        return data.get('user')

