import os
import sys
import yaml
import logging
from pathlib import Path
from pydantic import BaseModel

__ALL__ = ("get_config", "update_config", "config_logging", "Config")


class Config(BaseModel):
    class DBConfig(BaseModel):
        uri: str
        username: str = ""
        password: str = ""

    class CookiesConfig(BaseModel):
        aes_key: str  # Encryption key (must be 16, 24, or 32 bytes long)
        expire_sec: int

    class GreetingConfig(BaseModel):
        max_sessions: int
        expire_sec: int

    version: int
    debug: bool
    cookies: CookiesConfig
    greeting: GreetingConfig  # used for login & register
    logging: dict
    db: DBConfig


DEFAULT_CONFIG = Config.model_validate({
    "version": 2,
    "debug": True,
    "cookies": {
        "aes_key": "shiba_is_best&&$@SDU%^%#peropero",
        "expire_sec": 3600 * 24 * 7,  # 7 days
    },
    "greeting": {
        "max_sessions": 2048,
        "expire_sec": 300,
    },
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    },
    "db": {
        "uri": "sqlite:///shiba.db"
    }
})

CONFIG_PATH = Path(sys.modules["__main__"].__file__).parent / "config.yaml"
LOG_PATH = Path(sys.modules["__main__"].__file__).parent / "app.log"


def get_config() -> Config:
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG.model_dump(), f)
    with open(CONFIG_PATH) as f:
        config = Config.model_validate(yaml.safe_load(f))
    return config


def update_config(config: Config):
    if config.version < DEFAULT_CONFIG.version:
        os.rename(CONFIG_PATH, CONFIG_PATH.with_suffix(".bak"))
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG.model_dump(), f)
        print("Config file updated, old config file renamed to config.bak")
        sys.exit(0)


def config_logging(config: Config):
    logging.basicConfig(filename=LOG_PATH, **config.logging)

    if config.debug:
        logging.getLogger().addHandler(logging.StreamHandler())
