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

@views.route("/instructor-dashboard")
def instructorDashboard():
    return render_template("instructor-dashboard.html")

@views.route("/schedule-eval", methods=['POST', 'GET'])
def scheduleeval():
    sql = 'select co.offering_id, c.course_name from Course_Offering as co join Course as c on (c.course_id = co.course_id) where co.professor_id = %s'
    cursor.execute(sql, [userID])
    offerings = cursor.fetchall()

    if request.method == 'POST':
        selectedoffering = request.form.get('offering')

        sql = 'select distinct offering_id from Assignment where offering_id = %s'
        cursor.execute(sql, [selectedoffering])
        exists = cursor.fetchall()

        if len(exists) > 0:
            return evalexists()
        
        evalDate = request.form.get('date')
        evalTime = request.form.get('time')
        dateTime = f'{evalDate} {evalTime}'

        sql = 'select c.course_name from Course as c join Course_Offering as co on (c.course_id = co.course_id) where co.offering_id = %s'
        cursor.execute(sql, [selectedoffering])
        course = cursor.fetchone()

        sql = 'select s.student_id, s.name, s.email from Student_Course as sc join Student as s on (s.student_id = sc.student_id) where sc.Offering_ID = %s'
        cursor.execute(sql, [selectedoffering])
        students = cursor.fetchall()

        sql = 'select assignment_id from `Assignment` order by assignment_id desc limit 1'
        cursor.execute(sql)
        assignmentID = cursor.fetchone()

        for student in students:
            assignmentID['assignment_id'] += 1
            sql = 'insert into `Assignment` values (%s, %s, %s, %s, %s, 0)'
            cursor.execute(sql, [assignmentID['assignment_id'], selectedoffering, student['student_id'], date.today(), dateTime])
            dbconn.commit()
            # send_eval_assignment_email(student['email'], student['name'], course['course_name'])
        return evalscheduled()
    return render_template("schedule-eval.html", offerings=offerings)

@views.route("/eval-scheduled", methods=['GET'])
def evalexists():
    return render_template("eval-exists.html")

@views.route("/eval-exists", methods=['GET'])
def evalscheduled():
    return render_template("eval-scheduled.html")

@views.route("/course-created", methods=['GET'])
def coursecreated():
    return render_template("course-created.html")

@views.route("/course-updated", methods=['GET'])
def courseupdated():
    return render_template("course-updated.html")

@views.route("/group-created", methods=['GET'])
def groupcreated():
    return render_template("group-created.html")

@views.route("/group-modified", methods=['GET'])
def groupmodified():
    return render_template("group-modified.html")

@views.route("/group-deleted", methods=['GET'])
def groupdeleted():
    return render_template("group-deleted.html")

@views.route("/group", methods=['POST', 'GET'])
def group():
    sql = 'select co.offering_id, c.course_name from Course_Offering as co join Course as c on (c.course_id = co.course_id) where co.professor_id = %s'
    cursor.execute(sql, [userID])
    offerings = cursor.fetchall()
    if request.method == 'POST':
        if 'offering' in request.form:
            selectedoffering = request.form.get('offering')

            if 'csv_file' not in request.files:
                flash('No file part', category='error')
                return instructorportal()
            
            file = request.files['csv_file']

            if file.filename == '':
                flash('No selected file', category='error')
                return instructorportal()
            
            sql = 'select Group_ID from `Course_Groups` order by Group_ID desc limit 1'
            cursor.execute(sql)
            latest_group = cursor.fetchall()
            sql = 'insert into `Course_Groups`(Group_ID, Offering_ID) values(%s,%s)'
            cursor.execute(sql, [latest_group[0]['Group_ID'] + 1, selectedoffering])
            dbconn.commit()
            
            if file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_reader = csv.DictReader(stream)
                    for row in csv_reader:
                        sql = 'select student_id from Student where name = %s and email = %s'
                        cursor.execute(sql, [row['name'],row['email']])
                        result = cursor.fetchall()
                        sql = 'insert into `Student_Group`(group_id, offering_id, student_id) values(%s,%s,%s)'
                        cursor.execute(sql, [latest_group[0]['Group_ID'] + 1, selectedoffering, result[0]['student_id']])
                        dbconn.commit()
                        sql = 'select c.course_name from Course as c join Course_Offering as co on (c.course_id = co.course_id) where co.offering_id = %s'
                        cursor.execute(sql, [selectedoffering])
                        result = cursor.fetchall()
                        send_group_assignment_email(row['email'], row['name'], result[0]['course_name'])
                except Exception as e:
                    print(f'Error processing CSV file: {e}')
                return groupcreated()
            else:
                flash('Invalid file type. Please upload a CSV file.', category='error', offerings=offerings)
                return instructorportal()
        elif 'offering2' in request.form:
            selectedoffering = request.form.get('offering2')
            selectedgroup = request.form.get('groups')
            print(selectedgroup)

            if 'csv_file' not in request.files:
                flash('No file part', category='error')
                return instructorportal()
            
            file = request.files['csv_file']

            if file.filename == '':
                flash('No selected file', category='error')
                return instructorportal()
            
            sql = 'select Group_ID from `Course_Groups` order by Group_ID desc limit 1'
            cursor.execute(sql)
            latest_group = cursor.fetchall()
            
            if file and file.filename.endswith('.csv'):
                try:
                    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                    csv_reader = csv.DictReader(stream)
                    for row in csv_reader:
                        sql = 'select student_id from Student where name = %s and email = %s'
                        cursor.execute(sql, [row['name'],row['email']])
                        result = cursor.fetchall()
                        sql = 'insert into `Student_Group`(group_id, offering_id, student_id) values(%s,%s,%s)'
                        cursor.execute(sql, [selectedgroup, selectedoffering, result[0]['student_id']])
                        dbconn.commit()
                        sql = 'select c.course_name from Course as c join Course_Offering as co on (c.course_id = co.course_id) where co.offering_id = %s'
                        cursor.execute(sql, [selectedoffering])
                        result = cursor.fetchall()
                        send_group_assignment_email(row['email'], row['name'], result[0]['course_name'])
                except Exception as e:
                    print(f'Error processing CSV file: {e}')
                return groupmodified()
            else:
                flash('Invalid file type. Please upload a CSV file.', category='error', offerings=offerings)
                return instructorportal()
        else:
            selectedgroup = request.form.get('delete')

            sql = 'delete from `Course_Groups` where Group_ID = %s'
            cursor.execute(sql, selectedgroup)
            dbconn.commit()

            sql = 'delete from `Student_Group` where Group_ID = %s'
            cursor.execute(sql, selectedgroup)
            dbconn.commit()
            return groupdeleted()
    return render_template("group.html", offerings=offerings)

@views.route("/course-students", methods=['GET'])
def courseStudents():
    offeringID = request.args.get('ofid')
    sql = 'select sc.Student_ID, s.name, s.email from Student_Course as sc join Student as s on (sc.Student_ID = s.student_id) where offering_id = %s'
    cursor.execute(sql, [offeringID])
    students = cursor.fetchall()
    sql = 'select s.student_id, s.name, s.email, sg.group_id from `Student_Group` as sg join Student as s on (sg.student_id = s.student_id) where offering_id = %s'
    cursor.execute(sql, [offeringID])
    assigned = cursor.fetchall()
    return render_template("live-students.html", students=students, assigned=assigned)

@views.route("/students", methods=['GET'])
def students():
    offeringID = request.args.get('ofid')
    sql = 'select sc.Student_ID, s.name, s.email from Student_Course as sc join Student as s on (sc.Student_ID = s.student_id) where offering_id = %s'
    cursor.execute(sql, [offeringID])
    students = cursor.fetchall()
    return render_template("live-course.html", students=students)

@views.route("/existing-groups", methods=['GET'])
def coursegroups():
    offeringID = request.args.get('ofid')
    sql = 'select sc.Student_ID, s.name, s.email from Student_Course as sc join Student as s on (sc.Student_ID = s.student_id) where offering_id = %s'
    cursor.execute(sql, [offeringID])
    students = cursor.fetchall()
    sql = 'select s.student_id, s.name, s.email, sg.group_id from `Student_Group` as sg join Student as s on (sg.student_id = s.student_id) where offering_id = %s'
    cursor.execute(sql, [offeringID])
    assigned = cursor.fetchall()
    sql = 'select Group_ID from Course_Groups where Offering_ID = %s'
    cursor.execute(sql, [offeringID])
    groups = cursor.fetchall()
    return render_template("live-groups.html", students=students, assigned=assigned, groups=groups)

@views.route("/del-group", methods=['GET'])
def deletegroup():
    offeringID = request.args.get('ofid')
    sql = 'select Group_ID from Course_Groups where Offering_ID = %s'
    cursor.execute(sql, [offeringID])
    groups = cursor.fetchall()
    return render_template("delete-groups.html", groups=groups)

# @views.route("/course-groups", methods=['GET'])
# def courseGroups():
#     offeringID = request.args.get('ofid')
#     print(offeringID)
#     sql = 'select Group_ID from Course_Groups where Offering_ID = %s'
#     cursor.execute(sql, [offeringID])
#     groups = cursor.fetchall()
#     print(groups)
#     return render_template("live-groups.html", groups=groups)

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
                        sql = 'insert into `Student_Course`(Student_ID, Offering_ID) values(%s,%s)'
                        cursor.execute(sql, [result[0]['student_id'], selectedcourse])
                        dbconn.commit()
                        sql = 'select c.course_name from Course as c join Course_Offering as co on (c.course_id = co.course_id) where co.offering_id = %s'
                        cursor.execute(sql, [selectedcourse])
                        result = cursor.fetchall()
                        send_course_assignment_email(row['email'], row['name'], result[0]['course_name'])
                except Exception as e:
                    print(f'Error processing CSV file: {e}')
                return courseupdated()
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
                        sql = 'insert into `Student_Course`(Student_ID, Offering_ID) values(%s,%s)'
                        cursor.execute(sql, [result[0]['student_id'], offeringID[0]['offering_id'] + 1])
                        dbconn.commit()
                        print('test')
                        sql = 'select c.course_name from Course as c join Course_Offering as co on (c.course_id = co.course_id) where co.offering_id = %s'
                        cursor.execute(sql, [offeringID[0]['offering_id'] + 1])
                        result = cursor.fetchall()
                        send_course_assignment_email(row['email'], row['name'], result[0]['course_name'])
                except Exception as e:
                    print(f'Error processing CSV file: {e}')
                return coursecreated()
            else:
                flash('Invalid file type. Please upload a CSV file.', category='error', offerings=offerings)
                return redirect(request.url)
    return render_template("course.html", courses=courses, offerings=offerings)

@views.route("/eval-calender")
def evalCalender():
    sql = 'select distinct c.course_name, co.offering_id, co.semester, co.year, a.date_created, a.deadline, if(sum(a.completed) < count(a.offering_id), "Open", "Closed") as eval_status, sum(a.completed) as sum, count(a.offering_id) as count from Assignment as a join Course_Offering as co on (a.offering_id = co.offering_id) join Course as c on (co.course_id = c.course_id) join Professor as p on (co.professor_id = p.professor_id) where p.professor_id = %s group by a.offering_id'
    cursor.execute(sql, [userID])
    evals = cursor.fetchall()
    return render_template("eval-calender.html", evals=evals)

@views.route("/render-portal", methods=['GET'])
def renderinstructorportal():
    return instructorportal()

def send_course_assignment_email(student_email, student_name, course_name):
    message = Mail(
        from_email='annaschwarz@vt.edu',
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

def send_group_assignment_email(student_email, student_name, course_name):
    message = Mail(
        from_email='annaschwarz@vt.edu',
        to_emails=student_email,
        subject=f'Group Assignment Notification',
        html_content=f"""
            <p>Hi {student_name},</p>
            <p>You’ve been assigned a group in your <strong>{course_name}</strong> class.</p>
            <p>Best of luck!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {student_email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_eval_assignment_email(student_email, student_name, course_name):
    message = Mail(
        from_email='annaschwarz@vt.edu',
        to_emails=student_email,
        subject=f'Peer Evaluation Notification',
        html_content=f"""
            <p>Hi {student_name},</p>
            <p>You’ve been assigned a peer evaluation in your <strong>{course_name}</strong> class.</p>
            <p>Best of luck!</p>
        """
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"Email sent to {student_email}: {response.status_code}")
    except Exception as e:
        print(f"Failed to send email: {e}")