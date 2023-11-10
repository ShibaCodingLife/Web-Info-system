from flask import Flask, Response, request, render_template, jsonify, redirect, make_response
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from pydantic import BaseModel
from datetime import datetime
from functools import wraps
from .config import Config

__ALL__ = ("encrypt_cookies", "decrypt_cookies",
           "validate_cookies", "login_required", "Cookies")

config: Config
TeacherInfo: type


class Cookies(BaseModel):
    username: str
    token: str
    expire: datetime


def encrypt_cookies(cookies: Cookies) -> str:
    cipher = AES.new(config.cookies.aes_key.encode(), AES.MODE_GCM)
    encrypted, digest = cipher.encrypt_and_digest(
        cookies.model_dump_json().encode())
    data = len(digest).to_bytes(1, "little") + \
        digest + cipher.nonce + encrypted
    return b64encode(data).decode()


def decrypt_cookies(b64: str) -> Cookies:
    data = b64decode(b64)
    d_len = data[0]
    digest = data[1:1+d_len]
    cipher = AES.new(config.cookies.aes_key.encode(),
                     AES.MODE_GCM, nonce=data[d_len + 1:d_len + 17])
    decrypted: bytes = cipher.decrypt_and_verify(data[d_len + 17:], digest)
    cookies = Cookies.model_validate_json(decrypted.decode())
    return cookies


def validate_cookies(cookies: str | Cookies) -> bool:
    if isinstance(cookies, str):
        try:
            cookies = decrypt_cookies(cookies)
        except ValueError:
            return False

    teacher_info = TeacherInfo.query.filter_by(
        name=cookies.username, password=cookies.token).first()

    return teacher_info and cookies.expire > datetime.utcnow()


def login_required(default: Response = redirect("/login")):
    """
    A decorator that checks if the user is logged in by validating their cookies.
    If the user is not logged in, they are redirected to the login page.

    :param default: The default response to return if the user is not logged in.
    :return: The wrapped function.
    """
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            cookies = request.cookies.get("cookies")
            if not cookies or not validate_cookies(cookies):
                return default
            return func(*args, **kwargs)
        return wrapped
    return wrapper
