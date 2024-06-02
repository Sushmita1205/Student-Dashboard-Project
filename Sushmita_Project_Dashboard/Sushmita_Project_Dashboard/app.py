from flask import Flask, request, jsonify, render_template, Response, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
import numpy as np

app = Flask(__name__, '/static')
app.secret_key = "MyDashboard"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/test.db"
db = SQLAlchemy(app)
toastr = Toastr(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    attendance = db.Column(db.Integer, nullable=False)

    def __init__(self, course, gender, location, attendance):
        self.course = course
        self.gender = gender
        self.location = location
        self.attendance = attendance

@app.route('/submit', methods=['POST'])
def submit_student_data():
    try:
        data = request.get_json()
        student = Student(course=data['course'], gender=data['gender'], location=data['location'], attendance=data['attendance'])
        db.session.add(student)
        db.session.commit()
        flash("Data Submitted Successfully")
        return jsonify({
            'course': student.course,
            'gender': student.gender,
            'location': student.location,
            'attendance': student.attendance
        })
    except:
        flash("Unknown Error Occurred. Restart app & Try again")
    return jsonify({
        'course': "",
        'gender': "",
        'location': "",
        'attendance': ""
    })


@app.route('/analytics', methods=['GET', 'POST'])
def show_analytics():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'password123':
            max_att, min_att, mean_att = get_attendance()
            flash("Login Successful")
            return render_template('analytics.html', max_att=max_att, min_att=min_att, mean_att=mean_att)
        else:
            flash("Invalid Password! Please try again")
    return render_template('login.html')


def get_attendance():
    # Retrieve student data from database
    students = Student.query.all()

    # Process and analyze data
    attendance_rates = []
    for student in students:
        if (student.attendance != "" and student.attendance is not None):
            attendance_rates.append(int(student.attendance))

    if (len(attendance_rates) == 0):
        return 0, 0, 0

    numpy_array = np.array(attendance_rates)
    return numpy_array.max(), numpy_array.min(), numpy_array.mean()


@app.route('/student_distribution_gender.png')
def get_gender_chart():
    # Retrieve student data from database
    students = Student.query.all()

    # Process and analyze data
    male = 0
    female = 0
    neutral = 0
    for student in students:
        if (student.gender == 'Male'):
            male+=1
        elif (student.gender == 'Female'):
            female+=1
        elif (student.gender == 'Neutral'):
            neutral+=1

    # Create visualization
    fig, ax = plt.subplots()
    labels = 'Males', 'Females', 'Neutrals'
    sizes = [male, female, neutral]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title("Student Gender Distribution")
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/student_distribution_courses.png')
def get_courses_chart():
    # Retrieve student data from database
    students = Student.query.all()

    # Process and analyze data
    english = 0
    maths = 0
    science = 0
    for student in students:
        if (student.course == 'English'):
            english+=1
        elif (student.course == 'Maths'):
            maths+=1
        elif (student.course == 'Science'):
            science+=1

    # Create visualization
    fig, ax = plt.subplots()
    labels = 'English', 'Maths', 'Science'
    sizes = [english, maths, science]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    plt.title("Student Course Distribution")
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/student_distribution_days_per_course.png')
def get_courses_days_chart():
    # Retrieve student data from database
    students = Student.query.all()

    # Process and analyze data
    english_list = np.array([])
    maths_list = np.array([])
    science_list = np.array([])
    for student in students:
        if (student.course == 'English'):
            if (student.attendance != ''):
                english_list = np.append(english_list, int(student.attendance))
        elif (student.course == 'Maths'):
            if (student.attendance != ''):
                maths_list = np.append(maths_list, int(student.attendance))
        elif (student.course == 'Science'):
            if (student.attendance != ''):
                science_list = np.append(science_list, int(student.attendance))

    # Create visualization
    fig, ax = plt.subplots()
    labels = 'English', 'Maths', 'Science'
    values = [english_list.mean(), maths_list.mean(), science_list.mean()]
    plt.bar(labels, values, color ='maroon', 
        width = 0.4)
    plt.xlabel("Courses offered")
    plt.ylabel("Average attendance")
    plt.title("Course Attendance Distribution")
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='localhost', port=5002, debug=True)