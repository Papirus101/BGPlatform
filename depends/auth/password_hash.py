import hashlib
import os

from dotenv import load_dotenv

load_dotenv(".env")


async def hash_password(password: str):
    enc = hashlib.pbkdf2_hmac(
        f"{os.getenv('PASSWORD_ALGORITHM')}",
        password.encode(),
        os.getenv("SALT").encode(),
        100_000,
    )
    return enc.hex()


async def validate_password(password: str, hashed_password: str):
    return await hash_password(password) == hashed_password
