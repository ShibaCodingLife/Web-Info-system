import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

__ALL__ = ("init")


def init(config: Config):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")  # 初始化
    app.debug = config.debug
    app.config["SQLALCHEMY_DATABASE_URI"] = config.db.uri
    db = SQLAlchemy(app)

    class TeacherInfo(db.Model):  # 构造对象
        __tablename__ = "teacher_info"  # 定义是mysql中的哪一个表
        id = db.Column(db.Integer, primary_key=True)
        # 数据条定义,必须定义主键,否则flask会因在sqlite中找不到匹配模块而报错
        name = db.Column(db.String(100))
        password = db.Column(db.String(100))

    class TeacherStudentInfo(db.Model):
        __tablename__ = "teacher-stu"
        id = db.Column(db.Integer, primary_key=True)
        teachername = db.Column(db.String(100))
        studentname = db.Column(db.String(100))
        studentnumber = db.Column(db.String(100))
        studentsex = db.Column(db.String(100))
        studentage = db.Column(db.String(100))
        studentorigin = db.Column(db.String(100))
        studentsdept = db.Column(db.String(100))

    return app, db, TeacherInfo, TeacherStudentInfo
