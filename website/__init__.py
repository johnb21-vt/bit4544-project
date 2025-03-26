from flask import Flask
import os
import pymysql
import pymysql.cursors

# dbconn = pymysql.connect(
#     host = 'bit4544-test.cgr8msea0noj.us-east-1.rds.amazonaws.com',
#     port = 3306,
#     user = 'admin',
#     password = 'bit4544password',
#     database = 'bit4544-test-db',
#     cursorclass = pymysql.cursors.DictCursor
# )
dbconn = pymysql.connect(
    host = 'smu-db.chwcg66ko0iu.us-east-1.rds.amazonaws.com',
    port = 3306,
    user = 'admin',
    password = 'Password!',
    database = 'smu_db',
    cursorclass = pymysql.cursors.DictCursor
)
cursor = dbconn.cursor()

def create_app():
    app = Flask(__name__)
    app.secret_key = '726y3408756y2-0xs397465ynd02873t45s0'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app