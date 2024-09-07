from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
db = SQLAlchemy(app)
app.app_context().push()
#-----------------------------Tables----------------------------------------
class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, nullable=False, unique=True)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__="enrollments"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id"), nullable=False)

# db.create_all()
#-------------------------------CRUD OPERATIONS-----------------------------------------------------
@app.route('/')
def homepage():
    students = Student.query.all()
    return render_template("home.html", students = students)

@app.route('/student/create', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        r_no = request.form.get('roll')
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')

        std = db.session.query(Student).filter(Student.roll_number==r_no).first()
        if std is not None:
            return render_template("std_exist.html")
        student = Student(roll_number=r_no, first_name=f_name, last_name=l_name)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for("homepage"))
    return render_template("add_student.html")

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = db.session.query(Student).filter(Student.student_id==student_id).first()

    if request.method == 'POST':
        new_f_name = request.form.get('f_name')
        new_l_name = request.form.get('l_name')
        new_course = request.form.get('course') # course_code

        course = Course.query.filter_by(course_code=new_course).first()
        enrolled_courses = Enrollments.query.filter_by(estudent_id=student_id).all()

        if new_f_name != student.first_name:
            student.first_name = new_f_name
        if new_l_name != student.last_name:
            student.last_name = new_l_name
        
        if enrolled_courses == []:
            new_enroll = Enrollments(estudent_id=student.student_id, ecourse_id=course.course_id)
            db.session.add(new_enroll)
        else:
            flag = True
            for enroll in enrolled_courses:
                if enroll.ecourse_id == course.course_id:
                    flag = False
            if flag:
                new_enroll = Enrollments(estudent_id=student.student_id, ecourse_id=course.course_id)
                db.session.add(new_enroll)
        db.session.commit()
        return redirect(url_for('homepage'))

    courses = Course.query.all()
    return render_template("update_std.html", student=student, courses=courses)

@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
    student = db.session.query(Student).filter(Student.student_id==student_id).first()
    enrollment_list = db.session.query(Enrollments).filter(Enrollments.estudent_id==student_id).all()

    if enrollment_list != []:
        for enroll in enrollment_list:
            db.session.delete(enroll)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for("homepage"))

@app.route('/student/<int:student_id>')
def student_details(student_id):
    student = db.session.query(Student).filter(Student.student_id==student_id).first()
    enrollment_list = db.session.query(Enrollments).filter(Enrollments.estudent_id==student_id).all()
    courses = []
    if enrollment_list != []:
        for enroll in enrollment_list:
            course = db.session.query(Course).filter(Course.course_id==enroll.ecourse_id).first()
            courses.append(course)
    return render_template("std_details.html", student=student, courses=courses)

@app.route('/student/<int:student_id>/withdraw/<int:course_id>')
def course_remover(student_id, course_id):
    enrollment_list = Enrollments.query.filter_by(estudent_id=student_id).all()
    for enroll in enrollment_list:
        if enroll.ecourse_id == course_id:
            db.session.delete(enroll)
            db.session.commit()
    return redirect(url_for('homepage'))

@app.route('/courses')
def course_page():
    courses = Course.query.all()
    return render_template("course_home.html", courses=courses)

@app.route('/course/create', methods=['GET', 'POST'])
def course_creator():
    if request.method == 'POST':
        c_code = request.form.get('code')
        c_name = request.form.get('c_name')
        c_desc = request.form.get('desc')

        course_exist = Course.query.filter_by(course_code=c_code).first()
        if course_exist is not None:
            return render_template('course_exist.html')
        course = Course(course_code=c_code, course_name=c_name, course_description=c_desc)
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('course_page'))

    return render_template('add_course.html')

@app.route('/course/<int:course_id>/update', methods=['GET', 'POST'])
def course_updator(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    if request.method == 'POST':
        new_c_name = request.form.get('c_name')
        new_c_desc = request.form.get('desc')
        if course.course_name != new_c_name:
            course.course_name = new_c_name
        if course.course_description != new_c_desc:
            course.course_description = new_c_desc
        db.session.commit()
        return redirect(url_for('course_page'))
    return render_template('update_course.html', course=course)

@app.route('/course/<int:course_id>/delete')
def course_Delete(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('homepage'))

@app.route('/course/<int:course_id>')
def course_details(course_id):
    course = db.session.query(Course).filter(Course.course_id==course_id).first()
    enrolled_list = db.session.query(Enrollments).filter(Enrollments.ecourse_id==course_id).all()
    students = []
    for enroll in enrolled_list:
        student = db.session.query(Student).filter(Student.student_id==enroll.estudent_id).first()
        students.append(student)
    return render_template("course_details.html", course=course, students=students)

if __name__ == '__main__':
    app.run()