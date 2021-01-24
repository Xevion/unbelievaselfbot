from pprint import pprint

import discord


def print_embed(embed: discord.Embed) -> None:
    pprint((
        embed.title,
        embed.description,
        embed.footer,
        embed.color,
        embed.fields,
        embed.author,
        embed.timestamp
    ))
