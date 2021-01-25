import argparse
import logging

from bot import constants
from bot.client import UnbelievaClient


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the discord bot.')
    parser.add_argument('channel', metavar='CHANNEL', type=int,
                        help='The channel ID for the bot to target.')
    parser.add_argument('bot', metavar='BOT', type=int, help='The ID of the UnbelievaBoat bot to target.')

    parsed = parser.parse_args()

    logger = logging.getLogger(__file__)
    # noinspection PyArgumentList
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s',
                        handlers=[
                            logging.FileHandler(f"bot-{parsed.channel}.log", encoding='utf-8'),
                            logging.StreamHandler()
                        ])
    logger.setLevel(constants.LOGGING_LEVEL)

    client = UnbelievaClient(parsed.bot, parsed.channel)

    logger.info('Starting bot.')
    with open(constants.TOKEN, 'r') as file:
        token = file.read()
    client.run(token, bot=False)
