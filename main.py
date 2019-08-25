import discord
import json
import io
import compression
from db import db
from discordUtils import serverData, embeds
import encryption

# discord bot stuff
client = discord.Client()
config = json.load(open("./config.json"))
auth = lambda discord_id, server: discord_id in config["adminIds"] or server.owner.id == discord_id  # auth check
not_init = lambda channel: channel.send("The database is not initialized!")
# encryption related stuff
aes = encryption.AESCipher(config["aesPass"][:16].encode())


@client.event
async def on_ready():
    print(f"Ready! Running on user {client.user.name}#{client.user.discriminator}.")


@client.event
async def on_message(msg):
    if msg.author.bot:
        return
    if msg.content.startswith(config["prefix"]):
        db_guild = msg.guild
        msg_id = msg.author.id
        msg.content = msg.content[len(config["prefix"]):].split(" ")
        cmd = msg.content[0]
        if cmd == "init" and auth(msg_id, db_guild):
            for category in db_guild.categories:
                if category.name == "discord.fs":
                    for part in (await serverData.fs_location(db_guild, msg.channel)):
                        await part.delete()
            await serverData.init_fs(db_guild)
            await msg.channel.send(embed=embeds.embed_make("FS created!", "The file structure is ready.", msg.author))
        elif cmd == "remove" and auth(msg_id, db_guild):
            for part in await serverData.fs_location(db_guild, msg.channel):
                await part.delete()
            await msg.channel.send(
                embed=embeds.embed_make("FS removed!", "The file structure was removed.", msg.author))
        elif cmd == "upload":
            db_channel = await serverData.get_db(db_guild)
            if db_channel is None:
                not_init(msg.channel)
                return
            db_wrapper = db.Database(db_channel, aes)
            await msg.channel.send(embed=embeds.embed_make("Uploading...", "Please wait.", msg.author))
            attachments = []
            for attachment in msg.attachments:
                await db_wrapper.write_file(attachment.filename, await compression.compress(attachment), msg_id)
                attachments.append(attachment.filename)
            message = await msg.channel.send(
                embed=embeds.embed_make("File Uploaded!", "The file has uploaded.", msg.author, fields=[
                    (attachment, "Completed.") for attachment in attachments
                ]))
            await message.add_reaction("❌")
        elif cmd == "download":
            file_name = msg.content[1]
            db_channel = await serverData.get_db(db_guild)
            if db_channel is None:
                not_init(msg.channel)
                return
            db_wrapper = db.Database(db_channel, aes)
            file = await db_wrapper.get_file(file_name, msg_id)
            if not file:
                await msg.channel.send("You don't own this file or it doesn't exist!")
                return
            attachment = discord.File(io.BytesIO(compression.uncompress(file)), filename=file_name)
            message = await msg.channel.send(msg.author.mention, file=attachment)
            await message.add_reaction("❌")
        elif cmd == "help":
            prefix = config["prefix"]
            commands = [
                ("init",
                 "Creates the structure that allows discord.fs to function. (requires server owner or admin perms.)"),
                ("list", "List all files you own in the database."),
                ("download <file_name>", "Download a uploaded file you own from the database."),
                ("delete <file_name>", "Delete a file you own from the database."),
                ("remove", "Clears the database. (requires server owner or admin perms.)"),
                ("upload", "Upload an attachment to the database.")
            ]
            await msg.channel.send(embed=embeds.embed_make("Information.",
                                                           "discord.fs is a bot that emulates a filesystem on a discord channel. This allows for what is essentially free storage, without the privacy concerns. Using AES encryption, Discord cannot look at your files, even if they wanted to.",
                                                           msg.author, fields=commands))
        elif cmd == "delete":
            file_name = msg.content[1]
            db_channel = await serverData.get_db(db_guild)
            if db_channel is None:
                not_init(msg.channel)
                return
            db_wrapper = db.Database(db_channel, aes)
            await db_wrapper.delete_file(file_name, msg.author.id)

        elif cmd == "list":
            db_channel = await serverData.get_db(db_guild)
            if db_channel is None:
                not_init(msg.channel)
                return
            db_wrapper = db.Database(db_channel, aes)
            message = await msg.channel.send(
                embed=embeds.embed_make("File List.", "Here are your files in the database.", msg.author, [
                    file for file in await db_wrapper.get_file_names(msg.author.id)
                ]))
            await message.add_reaction("❌")


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author.id == client.user.id:
        if user in reaction.message.mentions:
            await reaction.message.delete()
        else:
            for embed in reaction.message.embeds:
                if str(user) == embed.footer.text:
                    print(reaction.message)
                    await reaction.message.delete()


client.run(config["token"])
