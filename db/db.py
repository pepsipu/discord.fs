class Database:
    def __init__(self, db, aes):
        self.db = db
        self.aes = aes

    async def write(self, plaintext):
        message = self.aes.encrypt(plaintext).decode()
        message_chunks = [message[i:i + 1999] for i in range(0, len(message), 1999)]
        for message_chunk in message_chunks:
            await self.db.send(message_chunk)

    async def write_file(self, filename, message, owner):
        await self.db.send(f"ä〜{self.aes.encrypt(filename).decode()}〜{self.aes.encrypt(str(owner)).decode()}")
        await self.write(message)
        await self.db.send("Ż")

    async def get_file(self, name, msg_id):
        getting_data = False
        data = ""
        async for message in self.db.history(oldest_first=True):
            if getting_data:
                if message.content == "Ż":
                    getting_data = False
                else:
                    data += message.content
            elif message.content.startswith("ä"):
                header = message.content.split("〜")
                if self.aes.decrypt(header[1]).decode() == name and self.aes.decrypt(header[2]).decode() == str(msg_id):
                    getting_data = True
        if data == "":
            return None
        return self.aes.decrypt(data).decode()

    async def delete_file(self, name, msg_id):
        remove = False
        async for message in self.db.history(oldest_first=True):
            if remove:
                await message.delete()
                if message.content == "Ż":
                    remove = False
            elif message.content.startswith("ä"):
                header = message.content.split("〜")
                if self.aes.decrypt(header[1]).decode() == name and self.aes.decrypt(header[2]).decode() == str(msg_id):
                    remove = True
                    await message.delete()

    async def get_file_names(self, msg_id):
        file_names = []
        async for message in self.db.history(oldest_first=True):
            if message.content.startswith("ä"):
                header = message.content.split("〜")
                if self.aes.decrypt(header[2]).decode() == str(msg_id):
                    file_names.append(
                        (self.aes.decrypt(header[1]).decode(), message.created_at.strftime('%l:%M%p %Z on %b %d, %Y')))
        return file_names
