import instagram_hack_api as iha
from .errors import InstagramRobotError
import robot.util as ru
import logging
import requests

logger = logging.getLogger('social_interface')

class Instagram:
    MAX_RETRY_COUNT = 5
    def __init__(self, cookies=None):
        self.api = iha.InstagramHackAPI(cookies=cookies)

    def try_call(self, callback, *args, **kwargs):
        retry_count = 0
        while(1):
            try:
                return callback(*args, **kwargs)
            except iha.CheckPointConfirm:
                self.integrity_checkpoint()
                continue
            except iha.InstagramHackAPIError as e:
                if retry_count > self.MAX_RETRY_COUNT:
                    logger.error('Max retries exceeded')
                    raise e
                if e.status_code == 500:
                    logger.error('Error 500. Sleeping.')
                    ru.simulate_wait(120)
                if e.status_code in [402, 407, 502, 503, 509]:
                    logger.error('Status {} returned. Likely to be a proxy error. Retrying'.format(e.status_code))
                    ru.simulate_wait(10)
                if e.status_code in [429, 403]:
                    logger.error('Forbidden response returned. Sleeping 120 seconds.')
                    ru.simulate_wait(120)
                else:
                    raise e
                retry_count += 1
            except requests.exceptions.SSLError:
                logger.error('SSL Error. Retrying..')
                ru.simulate_wait(1)

    def integrity_checkpoint(self):
        try:
            self.api.integrity_checkpoint()
        except iha.CheckPointConfirm:
            logger.info('Checkpoint confirmed')

    def fetch_paginated(self, paginated, delay_time=None):
        try:
            last_cursor = paginated.cursor
            while self.try_call(paginated.next_page):
                if not paginated.nodes:
                    break
                for node in paginated.nodes:
                    yield node, None, last_cursor
                if delay_time:
                    ru.simulate_wait(delay_time)
                last_cursor = paginated.cursor
        except iha.InstagramHackAPIError as e:
            yield node, e, last_cursor


    def fetch_follows(self, username=None, cursor=None, delay_time=None):
        if not self.api:
            raise InstagramRobotError('No api initialized')

        paginated = self.api.follows(username=username, cursor=cursor)
        return self.fetch_paginated(paginated, delay_time)

    def fetch_followers(self, username=None, cursor=None, delay_time=None):
        if not self.api:
            raise InstagramRobotError('No api initialized')

        paginated = self.api.followers(username=username, cursor=cursor)
        return self.fetch_paginated(paginated, delay_time)

    def fetch_user(self, username, delay_time=None):
        if not self.api:
            raise InstagramRobotError('No api initialized')

        api_user_call = lambda: self.api.user(username); ru.simulate_wait(delay_time) if delay_time else None
        return self.try_call(api_user_call)

    def follow(self, username, user_id, delay_time=None):
        if not self.api:
            raise InstagramRobotError('No api initialized')

        api_user_call = lambda: self.api.follow(username, user_id); ru.simulate_wait(delay_time) if delay_time else None
        return self.try_call(api_user_call)

    def unfollow(self, username, user_id, delay_time=None):
        if not self.api:
            raise InstagramRobotError('No api initialized')

        api_user_call = lambda: self.api.unfollow(username, user_id); ru.simulate_wait(delay_time) if delay_time else None
        return self.try_call(api_user_call)

    def authenticate(self, username, password):
        self.api.authenticate(username, password)
