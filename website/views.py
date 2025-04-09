from flask import Blueprint, render_template, request, flash, json, redirect, url_for
from jinja2 import TemplateNotFound
from website import dbconn, cursor
from datetime import date
import csv
import io
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

views = Blueprint('views', __name__)
userID = None

@views.route('/home', methods=['GET', 'POST'])
def home():
    assignmentid = request.args.get('assignmentid')
    sql = 'select name, student_id from `Student`'
    cursor.execute(sql)
    students = cursor.fetchall()
    if request.method == 'POST':
        studentid = request.form.get('studentid')
        selfeval = False
        if int(studentid) == int(userID):
            selfeval = True
        dk = int(request.form.get('options'))
        mk = int(request.form.get('options2'))
        ctps = int(request.form.get('options3'))
        ies = int(request.form.get('options4'))
        cl = int(request.form.get('options5'))
        c = int(request.form.get('options6'))
        ius = int(request.form.get('options7'))
        stdia = int(request.form.get('options8'))
        esr = int(request.form.get('options9'))
        sdml = int(request.form.get('options10'))
        rp = int(request.form.get('options11'))
        average = (dk+mk+ctps+ies+cl+c+ius+stdia+esr+sdml+rp)/11
        try:
            sql = 'select evaluation_id from `Peer_Evaluation` order by evaluation_id desc limit 1'
            cursor.execute(sql)
            result = cursor.fetchall()
            peereval_sql = 'insert into `Peer_Evaluation`(evaluation_id, evaluator_id, evaluatee_id, assignment_id, date_submitted, self_evaluation) values(%s,%s,%s,%s,CURRENT_TIMESTAMP,%s)'
            cursor.execute(peereval_sql, [result[0]['evaluation_id'] + 1, userID, studentid, assignmentid, selfeval])
            dbconn.commit()
            sql = 'select outcome_id from `Outcome` order by outcome_id desc limit 1'
            cursor.execute(sql)
            result2 = cursor.fetchall()
            outcome = 'insert into `Outcome`(outcome_id, evaluation_id, score) value(%s,%s,%s)'
            cursor.execute(outcome, [result2[0]['outcome_id'] + 1, result[0]['evaluation_id'] + 1, average])
            dbconn.commit()
            sql = 'update Assignment set completed = 1 where assignment_id = %s;'
            cursor.execute(sql, [assignmentid])
            dbconn.commit()
            return portal()
        except ValueError:
            flash('Commit failure, try again.', category='error')
    return render_template("home.html", students = students)

@views.route("/", methods=['POST', 'GET'])
def login():
    error = False
    global userID
    userID = None

    email = request.form.get('email')
    password = request.form.get('password')

    if not email:
        error = True
    if not password:
        error = True
    
    # Redirect back if there's an error
    if error == False: 
        cursor = dbconn.cursor()
        sql = "SELECT student_id FROM `Student` WHERE email = %s AND password = %s;"
        cursor.execute(sql, [email, password])
        results = cursor.fetchall()
        if results:
             userID = results[0]['student_id']
             return portal()
        else:
            sql = "SELECT professor_id FROM `Professor` WHERE email = %s AND password = %s;"
            cursor.execute(sql, [email, password])
            results = cursor.fetchall()
            if results:
                userID = results[0]['professor_id']
                return instructorportal()
            else:
                return loginfail()
    return render_template("login.html", userID = userID)

@views.route("/login-fail")
def loginfail():
    return render_template("login-fail.html")

@views.route("/portal")
def portal():
    sql = 'select c.course_name, co.course_id, a.offering_id, a.deadline, a.assignment_id, a.completed from `Course` as c left join `Course_Offering` as co on (c.course_id = co.course_id) left join `Assignment` as a on (co.offering_id = a.offering_id) where a.student_id = %s;'
    cursor.execute(sql, [userID])
    result = cursor.fetchall()
    print(result)
    return render_template("portal.html", assignments = result, userID = userID)

@views.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", userID = userID)

@views.route("/resetpassword", methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirmpassword')
        if confirm == password:
            sql = 'update `Student` as s set s.password = %s where s.email = %s'
            cursor.execute(sql, [password, email])
            dbconn.commit()
            return login()
    return render_template("password.html")

@views.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'student':
            sql = 'select student_id from `Student` order by student_id desc limit 1'
            cursor.execute(sql)
            result = cursor.fetchall()
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('passwordconfirm')
            if confirm == password:
                sql = 'insert into `Student`(student_id, name, email, password) values(%s, %s, %s, %s)'
                cursor.execute(sql, [result[0]['student_id'] + 1, name, email, password])
                dbconn.commit()
                return signupconfirm()
        else:
            sql = 'select professor_id from `Professor` order by professor_id desc limit 1'
            cursor.execute(sql)
            result = cursor.fetchall()
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm = request.form.get('passwordconfirm')
            if confirm == password:
                sql = 'insert into `Professor`(professor_id, name, email, password) values(%s, %s, %s, %s)'
                cursor.execute(sql, [result[0]['professor_id'] + 1, name, email, password])
                dbconn.commit()
                return signupconfirm()
    return render_template("signup.html")

@views.route("/signup-confirm")
def signupconfirm():
    if request.method == 'POST':
        return login()
    return render_template("signup-confirmation.html")

@views.route("/instructor-portal")
def instructorportal():
    return render_template("instructor-portal.html")

@views.route("/group")
def group():
    sql = 'select co.offering_id, c.course_name from Course_Offering as co join Course as c on (c.course_id = co.course_id) where co.professor_id = %s'
    cursor.execute(sql, [userID])
    offerings = cursor.fetchall()
    return render_template("group.html", offerings=offerings)

@views.route("/course", methods=['GET', 'POST'])
def course():
    sql = 'select co.offering_id, c.course_name from Course_Offering as co join Course as c on (c.course_id = co.course_id) where co.professor_id = %s'
    cursor.execute(sql, [userID])
    offerings = cursor.fetchall()

    sql = 'select course_id, course_name from Course'
    cursor.execute(sql)
    courses = cursor.fetchall()

    if request.method == 'POST':
        if 'offering' in request.form:
            selectedcourse = request.form.get('offering')

            if 'csv_file' not in request.files:
                flash('No file part', category='error')
                return redirect(request.url)
            
            file = request.files['csv_file']

            if file.filename == '':
                flash('No selected file', category='error')
                return redirect(request.url)
            
            if file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_reader = csv.DictReader(stream)
                    for row in csv_reader:
                        sql = 'select student_id from Student where name = %s and email = %s'
                        cursor.execute(sql, [row['name'],row['email']])
                        result = cursor.fetchall()
                        send_group_assignment_email(row['email'], row['name'], 'test course')
                        sql = 'insert into `Student_Course`(Student_ID, Offering_ID) values(%s,%s)'
                        cursor.execute(sql, [result[0]['student_id'], selectedcourse])
                        dbconn.commit()
                except Exception as e:
                    print(f'Error processing CSV file: {e}', category='error')
                return redirect(url_for('views.course')) 
            else:
                flash('Invalid file type. Please upload a CSV file.', category='error', offerings=offerings)
                return redirect(request.url)
        else:
            course = request.form.get('course')
            semester = request.form.get('semester')
            year = request.form.get('year')
            time = request.form.get('time')

            sql = 'select offering_id from `Course_Offering` order by offering_id desc limit 1'
            cursor.execute(sql)
            offeringID = cursor.fetchall()

            if 'csv_file' not in request.files:
                flash('No file part', category='error')
                return redirect(request.url)
            
            file = request.files['csv_file']

            if file.filename == '':
                flash('No selected file', category='error')
                return redirect(request.url)
            
            sql = 'insert into `Course_Offering`(offering_id, course_id, professor_id, semester, year, time) values (%s,%s,%s,%s,%s,%s)'
            cursor.execute(sql, [offeringID[0]['offering_id'] + 1, course, userID, semester, year, time])
            dbconn.commit()
            
            if file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_reader = csv.DictReader(stream)
                    for row in csv_reader:
                        sql = 'select student_id from Student where name = %s and email = %s'
                        cursor.execute(sql, [row['name'],row['email']])
                        result = cursor.fetchall()
                        send_group_assignment_email(row['email'], row['name'], 'test course')
                        sql = 'insert into `Student_Course`(Student_ID, Offering_ID) values(%s,%s)'
                        cursor.execute(sql, [result[0]['student_id'], offeringID[0]['offering_id'] + 1])
                        dbconn.commit()
                except Exception as e:
                    print(f'Error processing CSV file: {e}', category='error')
                return instructorportal()
            else:
                flash('Invalid file type. Please upload a CSV file.', category='error', offerings=offerings)
                return redirect(request.url)
    return render_template("course.html", courses=courses, offerings=offerings)

def send_group_assignment_email(student_email, student_name, course_name):
    message = Mail(
        from_email='johnb21@vt.edu',
        to_emails=student_email,
        subject=f'Group Assignment Notification',
        html_content=f"""
            <p>Hi {student_name},</p>
            <p>You’ve been assigned to the course <strong>{course_name}</strong>.</p>
            <p>Best of luck!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {student_email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")