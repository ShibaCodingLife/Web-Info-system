import os
import sys
import yaml
import logging
from pathlib import Path
from pydantic import BaseModel, Field

__ALL__ = ("get_config", "update_config", "config_logging", "Config")


class Config(BaseModel):
    class DBConfig(BaseModel):
        uri: str = "sqlite:///test.db"
        username: str = ""
        password: str = ""

    class CookiesConfig(BaseModel):
        # Encryption key (must be 16, 24, or 32 bytes long)
        aes_key: str = "shiba_is_best&&$@SDU%^%#peropero"
        expire_sec: int = 3600 * 24 * 7  # 7 days

    class GreetingConfig(BaseModel):
        max_sessions: int = 2048
        expire_sec: int = 300

    class ExperimentalConfig(BaseModel):
        ...

    version: int = 4
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    cookies: CookiesConfig = Field(default_factory=CookiesConfig)
    greeting: GreetingConfig = Field(default_factory=GreetingConfig)
    logging: dict = Field(default_factory=dict)
    db: DBConfig = Field(default_factory=DBConfig)
    experimental: ExperimentalConfig = Field(default_factory=ExperimentalConfig)


DEFAULT_CONFIG = Config()
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
LOG_PATH = Path(__file__).parent.parent / "app.log"


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
