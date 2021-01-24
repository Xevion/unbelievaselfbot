import asyncio
import sys
import time

import discord

client = discord.Client()
channel_id = 788214285712359475

last_message = time.time() - 5

# tasks = {
#     '$task': {
#         'duration': 13 * 60 + 5,
#         'last':
#     }
# }


async def income_task(task: str, minutes: int):
    global last_message
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    while not client.is_closed():
        # Sleep between commands
        wait_time = 7 - (time.time() - last_message)
        last_message = time.time()
        await asyncio.sleep(max(0.0, wait_time))

        await channel.send(task)
        await asyncio.sleep((minutes * 60) + 5)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.loop.create_task(income_task('$work', 5))
client.loop.create_task(income_task('$crime', 20))
client.loop.create_task(income_task('$slut', 13))

client.run(sys.argv[1], bot=False)
