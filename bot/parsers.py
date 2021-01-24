import logging
import re
from abc import ABC

import discord

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


class BaseMessage(object):
    """
    Abstract base class for message data parsing.
    """
    def __init__(self, message: discord.Message) -> None:
        self.message = message

    @classmethod
    def check_valid(cls, message: discord.Message) -> bool:
        """
        Check whether a message applies to this type of BaseMessage subclass.
        :return: True if this BaseMessage implementer works with the message.
        """
        raise NotImplementedError()


class EmbedMessage(BaseMessage, ABC):
    """
    A message that has a embed inside of it. Most messages are of this type.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embed = self.message.embeds[0]


class TaskCooldownMessage(EmbedMessage):
    COOLDOWN_REGEX = r'You cannot (work|be a slut|commit a crime) for ([\w\s]+)\.'
    DURATION_REGEX = r'(\d+) (hour|minute|second)s?(?: and (\d+) (hour|minute|second)s?)?'
    DELAY = 2

    durations = {'hour': 3600, 'minute': 60, 'second': 1}
    task_parsings = {'work': '$work', 'be a slut': '$slut', 'commit a crime': '$crime'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        match = re.search(TaskCooldownMessage.COOLDOWN_REGEX, self.embed.description)
        duration_match = re.match(TaskCooldownMessage.DURATION_REGEX, match.group(2))

        # Process the 1-2 groups found and calculate the duration
        self.duration = 0
        groups = len(list(filter(lambda s: s is not None, duration_match.groups())))
        for i in range(0, groups // 2):
            x, y = (i * 2) + 1, (i * 2) + 2
            self.duration += int(duration_match.group(x)) * TaskCooldownMessage.durations[duration_match.group(y)]

        self.task_type = TaskCooldownMessage.task_parsings[match.group(1)]
        self.available_at = self.message.created_at.timestamp() + TaskCooldownMessage.DELAY


class TaskResponse(EmbedMessage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change = 0

        money_match = re.search(r'\$([0-9,]+)', self.embed.description)
        if money_match and 'deposited' not in self.embed.description.lower():
            change = int(money_match.group(1).replace(',', ''))
            if self.embed.colour.value == 6732650:
                self.change += change
                # logger.info(f'Gained ${change}')
            if self.embed.colour.value == 15684432:
                self.change -= change
                # logger.info(f'Lost ${change}')
