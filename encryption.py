from Crypto.Cipher import AES
from Crypto import Random
import base64
import hashlib

pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[0:-s[-1]]


class AESCipher:

    def __init__(self, key):
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, raw):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b85encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b85decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))
