"""
parsers.py

Stores classes related to parsing and extracting information from different messages returned by UnbelievaBot.
"""

import logging
import re
from abc import ABC

import discord

from bot import constants

logger = logging.getLogger(__file__)
logger.setLevel(constants.LOGGING_LEVEL)


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
    COOLDOWN_REGEX = re.compile(r'You cannot (work|be a slut|commit a crime) for ([\w\s]+)\.')
    DURATION_REGEX = re.compile(r'(\d+) (hour|minute|second)s?(?: and (\d+) (hour|minute|second)s?)?')
    DELAY = 2

    __durations = {'hour': 3600, 'minute': 60, 'second': 1}
    __task_parsings = {'work': '$work', 'be a slut': '$slut', 'commit a crime': '$crime'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        match = re.search(TaskCooldownMessage.COOLDOWN_REGEX, self.embed.description)
        self.duration_unparsed = match.group(2)
        duration_match = re.match(TaskCooldownMessage.DURATION_REGEX, self.duration_unparsed)

        # Process the 1-2 groups found and calculate the duration
        self.duration = 0
        groups = len(list(filter(lambda s: s is not None, duration_match.groups())))
        for i in range(0, groups // 2):
            x, y = (i * 2) + 1, (i * 2) + 2
            self.duration += int(duration_match.group(x)) * TaskCooldownMessage.__durations[duration_match.group(y)]

        self.task_type = TaskCooldownMessage.__task_parsings[match.group(1)]
        self.available_at = self.message.created_at.timestamp() + self.duration + TaskCooldownMessage.DELAY

    @classmethod
    def check_valid(cls, message: discord.Message) -> bool:
        """Checks whether a Message object is a bot's income task cooldown response."""
        return len(message.embeds) > 0 \
               and message.embeds[0].description != discord.Embed.Empty \
               and message.embeds[0].description.startswith('<:stopwatch:630927808843218945> You cannot')


class TaskResponse(EmbedMessage):
    MONEY_REGEX = re.compile(r'\$([0-9,]+)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.change = 0
        money_match = re.search(TaskResponse.MONEY_REGEX, self.embed.description)

        if money_match:
            change = int(money_match.group(1).replace(',', ''))

            if self.embed.colour.value == 6732650:
                self.change += change
            elif self.embed.colour.value == 15684432:
                self.change -= change

    def log_message(self, name: str = None) -> str:
        return ('' if name is None else name + ' ') + ('Gained $' if self.change >= 0 else 'Lost $') + str(self.change)

    @classmethod
    def check_valid(cls, message: discord.Message) -> bool:
        """Checks that the message is a Bot Income Task response, denoting a amount of income or fine."""
        if len(message.embeds) > 0:
            embed = message.embeds[0]
            return embed.colour.value in [6732650, 15684432] \
                   and all(sub not in embed.description.lower() for sub in ['deposited', 'received your', 'withdrew']) \
                   and not embed.description.startswith('<:') \
                   and re.search(cls.MONEY_REGEX, embed.description) is not None

    def __repr__(self) -> str:
        return f'TaskResponse(change={self.change})'
