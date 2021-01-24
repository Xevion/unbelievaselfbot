class UnbelievableException(BaseException):
    pass


class BlackjackException(UnbelievableException):
    pass


class NoAceValue(BlackjackException):
    pass


class IndetermineValue(BlackjackException):
    pass
