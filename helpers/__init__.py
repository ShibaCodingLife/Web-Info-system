from . import config
from . import cookies
from . import database
from . import captcha
from . import search

__ALL__ = ("config", "cookies", "database", "captcha", "search", "init")


def init():
    cfg = config.get_config()
    config.update_config(cfg)
    config.config_logging(cfg)

    app, db, TeacherInfo, TeacherStudentInfo = database.init(cfg)

    cookies.config = cfg
    cookies.TeacherInfo = TeacherInfo

    return cfg, app, db, TeacherInfo, TeacherStudentInfo
