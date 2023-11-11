import io
import logging
import helpers
from math import ceil
from uuid import uuid4
from base64 import b64encode
from cachetools import TTLCache
from datetime import datetime, timedelta
from flask import request, render_template, jsonify, redirect, make_response
from helpers.cookies import login_required, validate_cookies
from helpers.cookies import decrypt_cookies, encrypt_cookies, Cookies
from helpers.captcha import generate_random_code, generate_image
from helpers.search import search_t_s_info

config, app, db, Student_base_info, Teacher_stu_info = helpers.init()

app.app_context().push()

code_map = TTLCache[str, str](
    maxsize=config.greeting.max_sessions,
    ttl=config.greeting.expire_sec)


@app.route('/')
def home():
    cookies = request.cookies.get("cookies")
    if not cookies or not validate_cookies(cookies):
        return redirect("/login")
    if config.experimental.replace_new_with_students:
        return redirect("/students")
    return redirect("/new.html")


@app.route("/login", methods=["GET"])
def login():
    captcha_code = generate_random_code()
    image = generate_image(captcha_code)
    b = io.BytesIO()
    image.save(b, "jpeg")
    image_path = f"data:image/jpeg;base64,{b64encode(b.getvalue()).decode()}"
    res = make_response(render_template("login.html", image_path=image_path))
    session_id = str(uuid4())
    res.set_cookie("session_id", session_id, httponly=True)
    code_map[session_id] = captcha_code.lower()
    return res


@app.route("/logout", methods=["GET"])
def logout():
    res = make_response(redirect("/login"))
    res.set_cookie("cookies", "", httponly=True)
    return res


@app.route("/login_get", methods=["POST"])  # 允许处理前端的post请求
def login_get():
    name = request.form.get("name")
    password = request.form.get("password")
    code = request.form.get("code")
    session_id = request.cookies.get("session_id")

    if not session_id:
        return redirect("/login")

    if not name or not password or not code:
        return jsonify({"success": False, "code": 1, "info": "信息不完整"})

    captcha_code = code_map.get(session_id)
    code = code.lower()

    if not captcha_code:
        return jsonify({"success": False, "code": 2, "info": "验证码过期"})

    if code != captcha_code:
        return jsonify({"success": False, "code": 3, "info": "验证码错误"})

    teacher_info = Student_base_info.query.filter_by(
        name=name, password=password).first()  # 查询过滤器

    logging.debug("Login attempt : name: %s, password: %s", name, password)

    if teacher_info:
        res = jsonify({"success": True, "info": "正确"})  # 封装信息并返回
        cookies = Cookies(
            username=name,
            token=password,
            expire=datetime.utcnow() + timedelta(seconds=config.cookies.expire_sec))
        res.set_cookie("cookies", encrypt_cookies(cookies), httponly=True)
        return res
    else:
        return jsonify({"success": False, "code": 4, "info": "教师信息错误"})


@app.route("/register_get", methods=["POST"])
def register_get():
    name = request.form.get("name")
    password = request.form.get("password")
    code = request.form.get("code")
    session_id = request.cookies.get("session_id")

    if not session_id:
        return redirect("/register")

    if not name or not password or not code:
        return jsonify({"success": False, "code": 1, "info": "信息不完整"})

    captcha_code = code_map.get(session_id)
    code = code.lower()

    if not captcha_code:
        return jsonify({"success": False, "code": 2, "info": "验证码过期"})

    if code != captcha_code:
        return jsonify({"success": False, "code": 3, "info": "验证码错误"})

    teacher_info = Student_base_info.query.filter_by(name=name).first()

    if teacher_info:
        return jsonify({"success": False, "code": 5, "info": "此用户已经存在"})

    new_student = Student_base_info(name=name, password=password)
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"success": True, "info": "注册成功"})


@app.route("/change_captcha")
def change_captcha():
    session_id = request.cookies.get("session_id")
    if not session_id:
        return jsonify({"success": False, "code": -1, "info": "未知错误, 请刷新界面"})
    code = generate_random_code()
    image = generate_image(code)
    code_map[session_id] = code.lower()
    b = io.BytesIO()
    image.save(b, "jpeg")
    image_path = f"data:image/jpeg;base64,{b64encode(b.getvalue()).decode()}"
    return jsonify({"success": True, "image_path": image_path})


@app.route("/new.html")  # 渲染此页面并查询所有带过的学生名单
@login_required()
def new_page():
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    name = cookies.username
    students = Teacher_stu_info.query.filter_by(teachername=name).all()
    return render_template("new.html", name=name, students=students)


@app.route("/login.html")  # 重定向,更新验证码,并更新全局变量code_num
def redirect_login():
    return redirect("/login")


@app.route("/register.html")  # 同样的更新
def redirect_register():
    return redirect("/register")


@app.route("/register")  # 同样的更新
def register_html():
    captcha_code = generate_random_code()
    image = generate_image(captcha_code)
    b = io.BytesIO()
    image.save(b, "jpeg")
    image_path = f"data:image/jpeg;base64,{b64encode(b.getvalue()).decode()}"
    res = make_response(render_template(
        "register.html", image_path=image_path))
    session_id = str(uuid4())
    res.set_cookie("session_id", session_id, httponly=True)
    code_map[session_id] = captcha_code.lower()
    return res


@app.route("/students", methods=["GET"])
@login_required()
def students():
    ITEMS_PER_PAGE = 7
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    page = request.args.get("page", 1, type=int) - 1
    name = cookies.username
    students = Teacher_stu_info.query.filter_by(teachername=name).all()
    total_pages = ceil(len(students) / ITEMS_PER_PAGE)

    if not total_pages:
        return render_template("students.html", teacher_name=name, students=[],
                               total_pages=1, this_page=1)

    if page < 0 or page >= total_pages:
        return redirect("/students?page=1")

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE if start + \
        ITEMS_PER_PAGE < len(students) else len(students)
    students = students[start:end]

    return render_template("students.html", teacher_name=name, students=students,
                           total_pages=total_pages, this_page=page + 1)


@app.route("/search/<search_input>", methods=["GET"])
@login_required()
def search(search_input):
    ITEMS_PER_PAGE = 7
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    page = request.args.get("page", 1, type=int) - 1
    name = cookies.username
    students = Teacher_stu_info.query.filter_by(teachername=name).all()
    total_pages = ceil(len(students) / ITEMS_PER_PAGE)

    if not total_pages:
        return render_template("students.html", teacher_name=name, students=[],
                               total_pages=1, this_page=1)

    if page < 0 or page >= total_pages:
        return redirect(f"/search/{search_input}?page=1")

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE if start + \
        ITEMS_PER_PAGE < len(students) else len(students)
    students = students[start:end]

    try:
        students = search_t_s_info(search_input, name, db, Teacher_stu_info)
    except ValueError as e:
        return render_template("students.html", teacher_name=name, students=[],
                               total_pages=total_pages, this_page=page + 1,
                               search_input=search_input, error=str(e))

    return render_template("students.html", teacher_name=name, students=students,
                           total_pages=total_pages, this_page=page + 1,
                           search_input=search_input)


@app.route("/all_get", methods=["POST"])  # 前端点击获取所有关于老师学生信息并渲染至表格中
@login_required(jsonify({"success": False, "code": 4401, "info": "请先登录"}))
def get_info():
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    name = cookies.username
    logging.debug("Get all info : name: %s", name)
    students = Teacher_stu_info.query.filter_by(teachername=name).all()
    student_list = [{"name": s.studentname, "number": s.studentnumber, "sex": s.studentsex,
                     "age": s.studentage, "origin": s.studentorigin, "sdept": s.studentsdept}
                    for s in students]  # 用你的实际字段替换
    return jsonify({"students": student_list})  # 以json格式返回


@app.route("/delete_student/<student_id>", methods=["DELETE"])  # 删除当前行学生
@login_required(jsonify({"success": False, "code": 4401, "info": "请先登录"}))
def delete_student(student_id):
    # 在数据库中查找该学号的学生
    student = Teacher_stu_info.query.filter_by(
        studentnumber=student_id).first()
    if student:
        db.session.delete(student)  # 删除学生记录
        db.session.commit()  # 提交更改
        # 将名字交给前端用于删除菜单左侧名单
        return jsonify({"success": True, "studentName": student.studentname})
    else:
        return jsonify({"success": False, "code": 4404, "info": "没有该学生信息"})


@app.route("/update_student/<student_id>", methods=["POST"])
@login_required(jsonify({"success": False, "code": 4401, "info": "请先登录"}))
def update_student(student_id):
    data = request.get_json()  # 获取json文件
    student = Teacher_stu_info.query.filter_by(
        studentnumber=student_id).first()

    logging.debug("Update student : student_id: %s, data: %s",
                  student_id, data)
    if student:
        try:
            student.studentnumber = data["number"]
            student.studentname = data["name"]
            student.studentage = data["age"]
            student.studentsex = data["sex"]
            student.studentorigin = data["address"]
            student.studentsdept = data["sdept"]
        except KeyError:
            return jsonify({"success": False, "code": 4402, "info": "信息不完整"})
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "code": 4404, "info": "没有该学生信息"})


@app.route("/add_student", methods=["POST"])
@login_required(jsonify({"success": False, "code": 4401, "info": "请先登录"}))
def add_student():
    data = request.get_json()
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    name = cookies.username

    try:
        new_stu = Teacher_stu_info(teachername=name, studentname=data["name"], studentnumber=data["number"],
                                   studentage=data["age"], studentsex=data["sex"],
                                   studentsdept=data["sdept"], studentorigin=data["address"],
                                   )
    except KeyError:
        return jsonify({"success": False, "code": 4402, "info": "信息不完整"})

    db.session.add(new_stu)
    db.session.flush()
    new_id = new_stu.studentnumber
    db.session.commit()
    return jsonify({"success": True, "student_id": new_id})


@app.route('/search-by-name', methods=['POST'])  # 通过学生姓名查询
@login_required(jsonify({"success": False, "code": 4401, "info": "请先登录"}))
def search_by_name():
    cookies = request.cookies.get("cookies")
    cookies = decrypt_cookies(cookies)
    name = cookies.username

    students = Teacher_stu_info.query.filter_by(studentname=name).all()
    if students:
        student_list = [{'name': s.studentname, 'number': s.studentnumber, 'sex': s.studentsex,
                         'age': s.studentage, 'origin': s.studentorigin, 'sdept': s.studentsdept}
                        for s in students]  # 用你的实际字段替换
        return jsonify({'success': True, 'student': student_list})
    else:
        return jsonify({'success': False, "code": 4404, "info": "没有该学生信息"})


if __name__ == "__main__":
    app.run()
