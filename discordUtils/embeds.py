import discord
import datetime


def embed_make(title, description, footer, fields=[],):
    embed = discord.Embed(title=title, description=description, color=0x02c6ff)
    embed.set_author(name="discord.fs", icon_url="https://i.imgur.com/2eWyRaX.png")
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=True)
    embed.set_footer(text=footer)
    embed.timestamp = datetime.datetime.today()
    return embed
