import requests
import logging
from .errors import raise_response_error
from .errors import CheckPointConfirm

logger = logging.getLogger('instagram_hack_api')

class HttpInterface:
    def __init__(self, cookies=None):
        self.session  = requests.Session()
        self.last_response = None
        if cookies is not None:
            self.session.cookies = cookies

    @property
    def cookies(self):
        return self.session.cookies

    def validate(f):
        def wrap(*args, **kwargs):
            response = f(*args, **kwargs)
            status_code = response.status_code
            if not (status_code == 200 or status_code == 302):
                logger.error('-------------------------')
                logger.error('Request Failed')
                logger.error('Request status: {}'.format(status_code))
                logger.error('Request url: {}'.format(response.request.url))
                logger.error('Request headers: {}'.format(response.request.headers))
                logger.error('Request data: {}'.format(response.request.body))
                logger.error('Response data: {}'.format(response.text))
                logger.error('Response headers: {}'.format(response.headers))
                logger.error('-------------------------')
                if status_code == 400:
                    logger.warning('*** WARNING: Max number of follows may have been reached or account temporarily blocked ***')
                raise_response_error(response)
            if response and response.cookies.get('checkpoint_step'):
                raise CheckPointConfirm('Checkpoint step required')
            return response
        return wrap

    @validate
    def get(self, *args, **kwargs):
        self.last_response = self.session.get(*args, **kwargs)
        return self.last_response

    @validate
    def post(self, *args, **kwargs):
        self.last_response = self.session.post(*args, **kwargs)
        return self.last_response
