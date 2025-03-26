from flask import Blueprint, render_template, request, flash, json, redirect, url_for
from jinja2 import TemplateNotFound
from website import dbconn, cursor
from datetime import date

views = Blueprint('views', __name__)

@views.route('/home', methods=['GET', 'POST'])
def home():
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
        print(average)
        try:
            sql = 'select evaluation_id from `Peer_Evaluation` order by evaluation_id desc limit 1'
            cursor.execute(sql)
            result = cursor.fetchall()
            peereval_sql = 'insert into `Peer_Evaluation`(evaluation_id, evaluator_id, evaluatee_id, assignment_id, date_submitted, self_evaluation) values(%s,%s,%s,%s,CURRENT_TIMESTAMP,%s)'
            cursor.execute(peereval_sql, [result[0]['evaluation_id'] + 1, 302, 302, 402, selfeval])
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

@views.route("/")
def login():
    return render_template("login.html")

@views.route("/portal")
def portal():
    return render_template("portal.html")

@views.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")