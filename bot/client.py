import argparse
import asyncio
import logging
import re
import time
from datetime import datetime
from pprint import pprint
from typing import Optional, Tuple

import discord
from discord.ext.tasks import loop

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


class UnbelievaClient(discord.Client):
    def __init__(self, bot_id: int, channel_id: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.last_message = -1

        self.bot_id, self.channel_id = bot_id, channel_id

        self.channel: Optional[discord.TextChannel] = None
        self.bot: Optional[discord.User] = None
        self.tasks = [
            ('$work', 5 * 60 + 5),
            ('$slut', 13 * 60 + 5),
            ('$crime', 20 * 60 + 5)
        ]
        self.task_times = {}
        self.durations = {
            'hour': 3600,
            'minute': 60,
            'second': 1
        }
        self.task_parsings = {
            'work': '$work',
            'be a slut': '$slut',
            'commit a crime': '$crime'
        }

        self.money = 0
        self.last_deposit = -1
        self.last_user_deposit = -1

    async def on_ready(self):
        await self.wait_until_ready()
        self.channel: discord.TextChannel = self.get_channel(self.channel_id)
        self.bot = self.bot_id
        self.check_task_available.start()
        logger.info(f'Connected to #{self.channel.name} in {self.channel.guild.name}')


    async def on_message(self, message: discord.Message):
        if message.channel == self.channel:
            if message.author.id == self.bot and len(message.embeds) > 0:
                embed = message.embeds[0]

                if embed.author.name == f'{self.user.name}#{self.user.discriminator}':
                    # Handling for task wait times
                    task_match = re.search(r'You cannot (work|be a slut|commit a crime) for ([\w\s]+)\.',
                                           embed.description)
                    if task_match:
                        self.handle_task_wait(task_match)

                    # Handling earnings
                    money_match = re.search(r'\$([0-9,]+)', embed.description)
                    if money_match and 'deposited' not in embed.description.lower():
                        change = int(money_match.group(1).replace(',', ''))
                        if embed.colour.value == 15684432:
                            self.money -= change
                            logger.info(f'Lost ${change}')
                        elif embed.colour.value == 6732650:
                            self.money += change
                            logger.info(f'Gained ${change}')

    def handle_task_wait(self, match: re.Match):
        task_command = self.task_parsings[match.group(1)]
        duration_match = re.match(
            r'(\d+) (hour|minute|second)s?(?: and (\d+) (hour|minute|second)s?)?',
            match.group(2))

        groups = len(list(filter(lambda s: s is not None, duration_match.groups())))
        duration = 0
        for i in range(0, groups // 2):
            x, y = (i * 2) + 1, (i * 2) + 2
            duration += int(duration_match.group(x)) * self.durations[duration_match.group(y)]
        epoch = time.time() + duration + 2
        logger.debug(f'"{match.group(2)}" => {duration}s')
        logger.debug(f'Changed {task_command} to wait {duration + 2}s instead.')
        self.task_times[task_command] = epoch

    @loop(seconds=1)
    async def check_task_available(self):
        await self.wait_until_ready()

        # Check for available tasks
        now = time.time()
        task_completed = False
        for task, duration in self.tasks:
            if self.task_times.get(task, 0) <= now:
                logger.debug(f'Planning to execute {task} {duration}s from now.')
                self.task_times[task] = now + duration
                await self.command_sleep()
                logger.debug(f'Executing {task} task.')
                await self.channel.send(task)
                self.last_message = time.time()
                task_completed = True

        if not task_completed:
            if self.last_deposit + (30 * 60) <= now:
                await self.command_sleep()
                await self.channel.send('$dep all')
                self.last_message = time.time()
                self.last_deposit = time.time()

    async def command_sleep(self):
        """Sleep right before sending a command."""
        now = time.time()
        time_between = now - self.last_message
        wait_time = 6 - time_between

        if wait_time > 0:
            logger.debug(f'Sleeping for {round(wait_time, 2)}s before sending a command...')
            await asyncio.sleep(wait_time)
