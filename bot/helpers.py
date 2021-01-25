from pprint import pprint
from typing import Union

import discord


def print_embed(embed: discord.Embed) -> None:
    """Helper method for printing out a complex Embed's entire set of possible attributes."""
    pprint((embed.title, embed.description, embed.footer, embed.color, embed.fields, embed.author, embed.timestamp))


def embed_author_matches(embed: discord.Embed, user: Union[discord.User, discord.ClientUser]):
    """Returns if the Unbelievabot Embed relates to the given user."""
    return embed.author != discord.embeds.EmptyEmbed and embed.author.name == f'{user.name}#{user.discriminator}'
