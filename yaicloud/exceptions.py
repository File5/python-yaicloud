class RequestFailed(Exception):
    pass


class AccountInvalidError(RequestFailed):
    pass


class AccountHackedError(RequestFailed):
    pass


class DiskAuthError(RequestFailed):
    pass
