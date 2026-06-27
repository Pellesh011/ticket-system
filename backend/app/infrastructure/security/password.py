import asyncio
import hashlib
import hmac
import os


async def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = await asyncio.to_thread(hashlib.pbkdf2_hmac, "sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    salt_hex, key_hex = hashed_password.split(":")
    salt = bytes.fromhex(salt_hex)
    expected_key = bytes.fromhex(key_hex)
    key = await asyncio.to_thread(hashlib.pbkdf2_hmac, "sha256", plain_password.encode(), salt, 100_000)
    return hmac.compare_digest(key, expected_key)
