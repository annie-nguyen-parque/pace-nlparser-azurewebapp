import time
import os
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
import psycopg2
from DBConnector import retrieve_data, close_db_connection
import QueryParser


DBUSER = 'admin'
DBPASS = 'supersecretpwd'
DBHOST = 'db'
DBPORT = '5432'
DBNAME = 'testdb'
con = None

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretpwd'


db = SQLAlchemy(app)


class students(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    gender = db.Column(db.String(50))
    major = db.Column(db.String(100))
    university = db.Column(db.String(100))

    def __init__(self, student_id, first_name, last_name, email, gender, major, university):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.major = major
        self.university = university


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()


def database_initialization_sequence():
    db.create_all()
    with open('data/students.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(students(row['student_id'], row['first_name'], row['last_name'],
                                    row['email'], row['gender'], row['major'], row['university']))

    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/query_data', methods=['GET', 'POST'])
def query_data():
    if request.method == 'POST':
        # Flash messages can be useful when the user interacts with the tool - i.e. success and error messages.
        # You can change the type of alert box displayed by changing the second argument according to Bootsrap's alert types:
        # https://getbootstrap.com/docs/4.3/components/alerts/
        flash('Hope this does something cool in the near future!', 'success')

        query = request.form.get('query')
        #result = retrieve_data(con, query)
        sql_query = QueryParser.create_query(query)
        try:
            result = retrieve_data(con, sql_query)
        except:
            try:
                result = retrieve_data(query)
            except:
                result = "Doesn't work"

        return render_template('query_data.html', students=result)


@app.route('/data')
def data():
    return render_template('show_all.html', students=students.query.all())


if __name__ == '__main__':
    dbstatus = False

    while dbstatus == False:
        try:
            db.create_all()
        except:
            time.sleep(2)
        else:
            dbstatus = True

    clear_data(db.session)
    database_initialization_sequence()
    con = psycopg2.connect(database="testdb", user="admin",
                                    password="supersecretpwd", host="db", port="5432")
    app.run(debug=True, host='0.0.0.0')
    close_db_connection(con)
