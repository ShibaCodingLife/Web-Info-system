from flask import Flask, request,render_template, jsonify,redirect#需要导入的包体,flask,request不用说,render_template用来渲染定位, jsonify是后端传给前端的数据格式以便前端获取其中的信息来做出判断,redirect重定向
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import io

app = Flask(__name__)#初始化
app.debug=True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:320421@localhost:3306/sakila'##数据库连接,在终端下载SQLAlchemy后用此命令连接,但有可能会出现mysql认证问题,所以建议再下一个cryptography 包,命令为pip install cryptography
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shiba.db'
db = SQLAlchemy(app)

global code_num
code_num=None

class Student_base_info(db.Model):#构造对象
    __tablename__ = 'teacher_info'#定义是mysql中的哪一个表
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))#数据条定义,必须定义主键,否则flask会因在sqlite中找不到匹配模块而报错
    password = db.Column(db.String(100))
    
class Teacher_stu_info(db.Model):
    __tablename__ = 'teacher-stu'
    id = db.Column(db.Integer, primary_key=True)
    teachername=db.Column(db.String(100))
    studentname =db.Column(db.String(100))
    studentnumber=db.Column(db.String(100))
    studentsex=db.Column(db.String(100))
    studentage=db.Column(db.String(100))
    studentorigin=db.Column(db.String(100))
    studentsdept=db.Column(db.String(100))

@app.route('/')
def home():
    code = generate_random_code()
    image = generate_image(code)
    global code_num
    code_num=code
    image_path = "static/captcha.png"
    image.save(image_path)
    return render_template('login.html', image_path=image_path, code=code)

# 显示登录页面，仅允许GET请求
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

    
@app.route('/login_get',methods=['POST'])#允许处理前端的post请求
def login_get():
    name=request.form.get('name')
    password=request.form.get('password')
    code=request.form.get('code')
     
    teacher_info=Student_base_info.query.filter_by(name=name,password=password).first()#查询过滤器
    print(name,password)
    if teacher_info:
        if code==code_num:
          return jsonify({"success":True,"info":"正确"})#封装信息并返回
        else:
            return jsonify({"success":False,"info":"验证码错误"})  
    else:
        return jsonify({"success":False,"info":"学生信息错误"})
    
@app.route('/register_get',methods=['POST']) 
def register_get():
    name=request.form.get('name')
    password=request.form.get('password')
    code=request.form.get('code')
     
    teacher_info=Student_base_info.query.filter_by(name=name).first()
    if teacher_info:
        return jsonify({"success":False,"info":"此用户已经存在"})  
    if code!=code_num:
       return jsonify({"success":False,"info":"验证码错误"})  
    else:
        new_student = Student_base_info(name=name, password=password)
        db.session.add(new_student)
        db.session.commit()
    return jsonify({"success": True, "info": "注册成功"})
        
    
def generate_random_code(length=4):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    code = ''.join(random.choice(characters) for _ in range(length))
    return code
    
def generate_image(code):
    image = Image.new('RGB', (150, 60), (255, 255, 255)) 
    draw = ImageDraw.Draw(image)

    # 使用艺术字体 
    font = ImageFont.truetype("arial.ttf", 40)

    for i in range(4):
        draw.text((10 + i * 30, 10), code[i], font=font, fill=(0, 0, 0))
        

    for _ in range(20):
        x1 = random.randint(0, 150)
        y1 = random.randint(0, 60)
        x2 = random.randint(0, 150)
        y2 = random.randint(0, 60)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0))

    for _ in range(30):
        x = random.randint(0, 150)
        y = random.randint(0, 60)
        draw.rectangle([x, y, x + 3, y + 3], fill=(0, 0, 0))

    for _ in range(500):
     x = random.randint(0, 150)
     y = random.randint(0, 60)
     r = random.randint(0, 255)
     g = random.randint(0, 255)
     b = random.randint(0, 255)
     draw.point((x, y), fill=(r, g, b))

    image = image.filter(ImageFilter.SMOOTH_MORE)
    return image

@app.route('/change_captcha')
def change_captcha():
    code = generate_random_code()
    image = generate_image(code)
    global code_num
    code_num=code
    image_path = "static/captcha.png"
    image.save(image_path)
    return jsonify({'image_path': image_path, 'code': code})

    
@app.route('/new.html')#渲染此页面并查询所有带过的学生名单
def new_page():
    name = request.args.get('name')
    students = Teacher_stu_info.query.filter_by(teachername=name).all()
    return render_template('new.html',name=name,students=students)

@app.route('/login.html')#重定向,更新验证码,并更新全局变量code_num
def new_page2():
    code = generate_random_code()
    image = generate_image(code)
    global code_num
    code_num=code
    image_path = "static/captcha.png"
    image.save(image_path)
    return render_template('login.html',image_path=image_path, code=code)

@app.route("/register.html")#同样的更新
def new_html():
    code = generate_random_code()
    image = generate_image(code)
    global code_num
    code_num=code
    image_path = "static/captcha.png"
    image.save(image_path)
    return render_template('register.html',image_path=image_path, code=code)

@app.route("/all_get",methods=['POST'])#前端点击获取所有关于老师学生信息并渲染至表格中
def get_info():
     name = request.form.get('name')
     print(name)
     students = Teacher_stu_info.query.filter_by(teachername=name).all()
     student_list = [{'name': student.studentname,'number':student.studentnumber,'sex':student.studentsex,'age':student.studentage,'origin':student.studentorigin,'sdept':student.studentsdept} for student in students]  # 用你的实际字段替换
     return jsonify({'students':student_list})#以json格式返回
     
@app.route('/delete_student', methods=['POST'])#删除当前行学生
def delete_student():
    student_number = request.form.get('student_number')
    # 在数据库中查找该学号的学生
    student = Teacher_stu_info.query.filter_by(studentnumber=student_number).first()
    if student:
        db.session.delete(student)  # 删除学生记录
        db.session.commit()  # 提交更改
        return jsonify({'success': True,'studentName': student.studentname})#将名字交给前端用于删除菜单左侧名单
    else:
        return jsonify({'success': False, 'error': '删除错误'})

@app.route('/update_student/<student_id>', methods=['POST'])
def update_student(student_id):
    data = request.get_json()#获取json文件
    student = Teacher_stu_info.query.filter_by(studentnumber=student_id).first()
    print(student_id)
    print(data['number'],data['age'],data['address'], data['sdept'])
    print(student.studentnumber,student.studentage)
    if student:
        student.studentnumber = data['number']
        student.studentage = data['age']
        student.studentorigin = data['address']
        student.studentsdept = data['sdept']
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 404


if __name__ == '__main__':
    app.run()