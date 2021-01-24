import argparse
import logging

from bot.client import UnbelievaClient

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s')
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the discord bot.')
    parser.add_argument('channel', metavar='CHANNEL', type=int,
                        help='The channel ID for the bot to target.')
    parser.add_argument('bot', metavar='BOT', type=int, help='The ID of the UnbelievaBoat bot to target.')

    parsed = parser.parse_args()
    client = UnbelievaClient(parsed.bot, parsed.channel)

    logger.info('Starting bot.')
    with open('../token.dat', 'r') as file:
        token = file.read()
    client.run(token, bot=False)
