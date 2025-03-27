from flask import Blueprint, render_template, request, flash, json, redirect, url_for
from jinja2 import TemplateNotFound
from website import dbconn, cursor
from datetime import date

views = Blueprint('views', __name__)
userID = None

@views.route('/home', methods=['GET', 'POST'])
def home():
    print(userID)
    if request.method == 'POST':
        studentname = request.form.get('studentname')
        selfeval = request.form.get('selfeval')

        if selfeval == None:
            selfeval = False
        else:
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
        print('TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST')
        try:
            sql = 'select evaluation_id from `Peer_Evaluation` order by evaluation_id desc limit 1'
            cursor.execute(sql)
            result = cursor.fetchall()
            peereval_sql = 'insert into `Peer_Evaluation`(evaluation_id, evaluator_id, evaluatee_id, assignment_id, date_submitted, self_evaluation) values(%s,%s,%s,%s,CURRENT_TIMESTAMP,%s)'
            cursor.execute(peereval_sql, [result[0]['evaluation_id'] + 1, userID, 302, 402, selfeval])
            dbconn.commit()
            sql2 = 'select outcome_id from `Outcome` order by outcome_id desc limit 1'
            cursor.execute(sql2)
            result2 = cursor.fetchall()
            outcome = 'insert into `Outcome`(outcome_id, evaluation_id, score) value(%s,%s,%s)'
            cursor.execute(outcome, [result2[0]['outcome_id'] + 1, result[0]['evaluation_id'] + 1, average])
            dbconn.commit()
        except ValueError:
            flash('Commit failure, try again.', category='error')
    return render_template("home.html")

@views.route("/", methods=['POST', 'GET'])
def login():
    error = False
    global userID
    userID = None

    studentemail = request.form.get('studentemail')
    studentpassword = request.form.get('studentpassword')

    if not studentemail:
        error = True
        flash("Please enter your email.")
    if not studentpassword:
        error = True
        flash("Please enter your password.")
    
    # Redirect back if there's an error
    if error == False: 
        cursor = dbconn.cursor()
        sql = "SELECT student_id FROM `Student` WHERE email = %s AND password = %s;"
        cursor.execute(sql, [studentemail, studentpassword])
        results = cursor.fetchall()
        if results:
             userID = results[0]['student_id']
             print(userID)
             return portal()
    return render_template("login.html", userID = userID)

@views.route("/portal")
def portal():
    sql = 'select c.course_name, co.course_id, a.offering_id, a.deadline from `Course` as c left join `Course_Offering` as co on (c.course_id = co.course_id) left join `Assignment` as a on (co.offering_id = a.offering_id) where a.student_id = %s;'
    cursor.execute(sql, [userID])
    result = cursor.fetchall()
    print(result)
    print('TEST TEST TEST TEST TEST')
    return render_template("portal.html", assignments = result, userID = userID)

@views.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")