from requests.auth import AuthBase


class YouTrackAuth(AuthBase):
    pass


class PasswordAuth(YouTrackAuth):
    pass


class Oauth2Auth(YouTrackAuth):
    pass


class TokenAuth(YouTrackAuth):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer {}'.format(self.token)
        return r
