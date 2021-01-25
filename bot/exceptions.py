"""
exceptions.py

Stores exceptions in a single file for the rest of the project to use.
"""


class UnbelievableException(BaseException):
    """Base project-wide exception"""
    pass


class BlackjackException(UnbelievableException):
    """Blackjack related exceptions inherit from this"""
    pass


class NoAceValue(BlackjackException):
    """The card was an ace and the program tried to acquire it's value - this should have been handled differently."""
    pass


class IndeterminateValue(BlackjackException):
    """The card's value could not be determined (likely a invalid card, or case sensitivity was ignored)."""
    pass


class InvalidCard(BlackjackException):
    """The card was fundamentally impossible in it's identifier."""
    pass


class CooldownRequired(UnbelievableException):
    """The program tried to activate/use a cooldown before it had ended."""
    pass
