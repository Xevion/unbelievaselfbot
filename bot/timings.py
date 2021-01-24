import time
from typing import Union, Optional

from bot import exceptions


class Cooldown(object):
    """
    A cooldown object helps users manage a minimum time passed between activations of something.
    """

    def __init__(self, cooldown: float, now: bool = False, last_hit: Union[float, int] = None):
        self.cooldown: float = max(0.0, cooldown)
        self.hot_until: Optional[float] = float(last_hit) if last_hit is not None else None

        if now:
            self.hot_until = time.time()

    def hit(self, safe: bool = False):
        """Activate the cooldown. Raises an exception if Safe is set to True and the cooldown has not passed."""
        if safe and not self.ready:
            raise exceptions.CooldownRequired('The cooldown duration has not passed. {}')
        self.hot_until = time.time() + self.cooldown

    @property
    def time_left(self) -> float:
        """Returns the non-negative time left until the cooldown is ready."""
        return max(0.0, self.hot_until - time.time())

    @property
    def ready(self, now: Union[float, int] = None) -> bool:
        """Returns True if the cooldown has passed."""
        if self.hot_until:
            return now or time.time() >= self.hot_until
        return True


class TimingHandler(object):
    """A class for easily managing and working with cooldown timers."""
    pass
