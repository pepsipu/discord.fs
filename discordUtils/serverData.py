import discord


async def get_db(guild):
    for channel in guild.channels:
        if channel.name == "db":
            return channel
    return None


async def get_category(guild, msg_channel):
    for category in guild.categories:
        if category.name == "discord.fs":
            return category
    await msg_channel.send("The database is not set up! Do db!init to initialize the database.")
    return None


async def fs_location(guild, msg_channel):
    return await get_db(guild), await get_category(guild, msg_channel)


async def init_fs(guild):
    db_category = await guild.create_category("discord.fs", overwrites={
        guild.default_role: discord.PermissionOverwrite(read_messages=False)
    })
    await guild.create_text_channel("db", category=db_category)
