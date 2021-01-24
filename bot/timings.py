import asyncio
import logging
import time
from datetime import datetime
from typing import Union, Optional

from bot import exceptions, constants

logger = logging.getLogger(__file__)
logger.setLevel(constants.LOGGING_LEVEL)


class Cooldown(object):
    """
    A cooldown object helps users manage a minimum time passed between activations of something.
    """

    def __init__(self, cooldown: float, now: bool = False, last_hit: Union[float, int] = None):
        self.cooldown: float = max(0.0, cooldown)
        self.hot_until: Optional[float] = float(last_hit) if last_hit is not None else None

        if now:
            self.hot_until = datetime.utcnow().timestamp()

    def hit(self, safe: bool = False):
        """Activate the cooldown. Raises an exception if Safe is set to True and the cooldown has not passed."""
        if safe and not self.ready:
            raise exceptions.CooldownRequired('The cooldown duration has not passed. {}')
        self.hot_until = datetime.utcnow().timestamp() + self.cooldown

    def change_expiration(self, timestamp: Union[float, int]) -> None:
        """
        Change the epoch timestamp at which the cooldown's hot period expires.
        :param timestamp: A epoch timestamp.
        """
        if self.hot_until is not None:
            change = round(abs(timestamp - self.hot_until), 2)
            change_word = 'longer' if timestamp > self.hot_until else 'sooner'
            logger.debug(f'Changing cooldown timestamp to {round(timestamp, 2)} ({change}s {change_word})')
        else:
            change = round(abs(timestamp - datetime.utcnow().timestamp()), 2)
            change_word = 'in the future' if timestamp >= datetime.utcnow().timestamp() else 'ago'
            logger.debug(f'Setting cooldown timestamp to {round(timestamp, 2)} ({change}s {change_word})')
        self.hot_until = timestamp

    async def sleep(self) -> None:
        if self.ready:
            return
        logger.debug(f'Sleeping for {self.time_left} before sending a command.')
        await asyncio.sleep(self.time_left)

    @property
    def time_left(self) -> float:
        """Returns the non-negative time left until the cooldown is ready."""
        return max(0.0, self.hot_until - datetime.utcnow().timestamp())

    @property
    def ready(self, now: Union[float, int] = None) -> bool:
        """Returns True if the cooldown has passed."""
        if self.hot_until:
            return now or datetime.utcnow().timestamp() >= self.hot_until
        return True


class TimingHandler(object):
    """A class for easily managing and working with cooldown timers."""
    pass
