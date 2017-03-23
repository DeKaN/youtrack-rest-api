class YouTrackException(Exception):
    message = None

    def __init__(self, message):
        self.message = message


class UnauthorizedYouTrackException(YouTrackException):
    pass


class ForbiddenYouTrackException(YouTrackException):
    pass


class NotFoundYouTrackException(YouTrackException):
    pass
