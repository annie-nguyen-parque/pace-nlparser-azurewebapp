import time
import os
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
import psycopg2
from DBConnector import retrieve_data, close_db_connection, nan_to_null, string_to_int, drop_tables
import QueryParser
#looks legit
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import *

#looks legit second
from  sqlalchemy import Table, Column, Integer, String, MetaData
MetaData = MetaData()
from sqlalchemy.orm import mapper

#maybe
from sqlalchemy import cast, select, String
import warnings




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


class top_students(db.Model):
    __tablename__ = 'top_students'
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


class university_ranking(db.Model):
    __tablename__ = 'university_rankings'
    university = db.Column(db.String(100), primary_key=True)
    location = db.Column(db.String(100))
    rank = db.Column(db.Integer)
    description = db.Column(db.String(10000))
    tuition_fees = db.Column(db.Integer)

    # in_state = db.Column()
    # in_state.type = in_state.type.evaluates_none()
    in_state = db.Column(db.Integer, nullable=True)

    undergrad_enrollment = db.Column(db.Integer)

    def __init__(self, university, location, rank, description, tuition_fees, in_state, undergrad_enrollment):
        self.university = university
        self.location = location
        self.rank = rank
        self.description = description
        self.tuition_fees = tuition_fees
        self.in_state = in_state
        self.undergrad_enrollment = undergrad_enrollment


class university_majors(db.Model):
    __tablename__ = 'university_majors'
    major_code = db.Column(db.Integer)
    major = db.Column(db.String(100), primary_key=True)
    major_category = db.Column(db.String(100))

    def __init__(self, major_code, major, major_category):
        self.major_code = major_code
        self.major = major
        self.major_category = major_category



def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()


def database_initialization_sequence():
    db.create_all()

    with open('data/top_students.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(top_students(row['Student ID'], row['First Name'], row['Last Name'],
                                    row['Email'], row['Gender'], row['Major'], row['University']))
    db.session.commit()

    with open('data/majors.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(university_majors(row['Major Code'], row['Major'], row['Major Category']))
    db.session.commit()

    nan_to_null('data/national_university_ranking.csv')
    with open('data/national_university_ranking.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(university_ranking(row['University'], row['Location'], row['Rank'],
                                    row['Description'], row['Tuition and fees'], row['In-state'], row['Undergrad Enrollment']))
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
        
        #flash('Hope this does something cool in the near future!', 'success')

        # query = request.form.get('query')
        # headerResult = QueryParser.create_query(query) 
        # sql_query = headerResult[0]
        # list = headerResult[1]
        # try:
        #     result = retrieve_data(con, sql_query)
        #     result.insert(0, list)
        #     print('no')
        # except:
        #     try:
        #         con.reset()
        #         print('yes')
        #         result = retrieve_data(con, query)
        #         print(result)
        #     except:
        #         con.reset()
        #         result = " "
        #         flash('Invalid Query, Soz', 'danger')

        # return render_template('query_data.html', students=result)
        query = request.form.get('query')
        print(query)
        #result = retrieve_data(con, query)
        
        sql_query = QueryParser.create_query(query)
        try:
            result = retrieve_data(con, sql_query)
        except:
            try:
                con.reset()
                result = retrieve_data(con, query)
            except:
                con.reset()
                result = "Invalid Query"

        return render_template('query_data.html', results=result)


@app.route('/data')
def data():
    return render_template('show_all.html', 
                            students=top_students.query.all(), 
                            majors=university_majors.query.all(),
                            national_university_ranking=university_ranking.query.all())


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

    con = psycopg2.connect(database="testdb", user="admin",
                                    password="supersecretpwd", host="db", port="5432")
    cursor = con.cursor()
    drop_tables(con, cursor, db)
    database_initialization_sequence()
    # drop_tables(con, cursor, db)
    app.run(debug=True, host='0.0.0.0')
    close_db_connection(con)
