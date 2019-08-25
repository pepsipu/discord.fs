import zlib
import base64


async def compress(file):
    return base64.b85encode(zlib.compress(await file.read(), level=9)).decode()


def uncompress(file):
    return zlib.decompress(base64.b85decode(file.encode()))
