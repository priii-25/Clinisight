from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

class Encryptor:
    def __init__(self, key):
        self.key = key.ljust(32)[:32].encode('utf-8')

    def encrypt(self, data):
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        return base64.b64encode(nonce + ciphertext).decode('utf-8')

    def decrypt(self, encrypted_data):
        raw = base64.b64decode(encrypted_data)
        nonce = raw[:16]
        ciphertext = raw[16:]
        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(ciphertext).decode('utf-8')