import json
from .variables import PROFILE_HTML
from .variables import PROFILE_URL
from .variables import CORE_HEADERS
from .variables import AJAX_HEADERS
from .variables import QUERY_URL


class Paginated:
    def __init__(self, http, username, cursor=None):
        self.http = http

        # Get profile
        profile_response = self.http.get(PROFILE_URL.format(username))
        data = json.loads(profile_response.text)
        user = data.get('user')
        cookies = self.http.session.cookies

        self.allowed = (not user.get('is_private') or 
                       (user.get('is_private') and user.get('followed_by_viewer')) or
                       user.get('id') == cookies.get('ds_user_id'))

        if self.allowed:
            csrftoken = cookies.get('csrftoken')
            self.request_headers = CORE_HEADERS.copy()
            self.request_headers.update({
                'x-csrftoken': csrftoken,
                'referer': PROFILE_HTML.format(username)
            })
            self.request_headers.update(AJAX_HEADERS)

        self.user_id       = user.get('id')
        self.last_response = None
        self.response_data = None
        self.nodes         = []
        self.has_next_page = True
        self.cursor        = cursor

    def next_page(self):
        if not self.allowed:
            return False
        if not self.has_next_page:
            return False

        query_data = {}
        query_data['query_id'] = self.QUERY_ID
        query_data['id'] = self.user_id
        query_data['first'] = 20
        if self.cursor:
            query_data['after'] = self.cursor

        response = self.http.get(QUERY_URL, 
                                  params=query_data, 
                                  headers=self.request_headers)
        self.last_response = response
        self.response_data = json.loads(response.text)
        envelope           = self.response_data.get('data')\
                               .get('user')\
                               .get(self.EDGE_NAME)
        self.nodes         = [edge.get('node') for edge in envelope.get('edges')]
        page_info          = envelope.get('page_info')
        self.has_next_page = page_info and page_info.get('has_next_page')
        self.cursor        = page_info and page_info.get('end_cursor')
        return True


class Followers(Paginated):
    EDGE_NAME = 'edge_followed_by'
    QUERY_ID = '17851374694183129'


class Follows(Paginated):
    EDGE_NAME = 'edge_follow'
    QUERY_ID = '17874545323001329'
