import json

class InstagramHackAPIError(Exception):
    def __init__(self, message, response=None, json_response=None):
        super().__init__(message)
        self.message        = message
        self.status_code    = response is not None and response.status_code
        self.response       = response
        self.json_response  = json_response


class CheckPointConfirm(Exception): pass


class CheckPointRequired(Exception):
    def __init__(self, check_point_url, lock):
        super().__init__(message)
        self.check_point_url = check_point_url
        self.lock            = lock


def raise_response_error(response):
    is_json = (response and response.headers 
               and response.headers.get('content-type') == 'application/json')
    json_response = json.loads(response.text) if is_json else None
    check_point_required = (response.status_code==400 and json_response
                            and json_response.get('message') == 'checkpoint_required')
    if check_point_required:
        checkpoint_url = json_response.get('checkpoint_url')
        lock           = json_response.get('lock')
        raise CheckPointRequired(checkpoint_url, lock)
    else:
        msg = response.text or 'Instagram responded with status code {}'.format(response.status_code)
        raise InstagramHackAPIError(msg, response, json_response)
