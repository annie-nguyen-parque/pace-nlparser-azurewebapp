import time
import os
import json
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
import psycopg2
from DBConnector import retrieve_data, close_db_connection, get_table_list, get_columns_names, drop_tables
import QueryParser
import parser


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

    # nan_to_null('data/national_university_ranking.csv')
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
        
        query = request.form.get('query')
        #headerResult: [0] - The query generated from QueryParser, 
        # [1] - The list of column names to use as Headers in top row
        # [2] - The list of tables that are used. 
        print(query)
        headerResult = parser.parse(query)
        sql_query = headerResult[0]
        print(sql_query)
        headerList = headerResult[1]
        tableList = headerResult[2]
        try:
            result = retrieve_data(con, cursor, sql_query)
            result.insert(0, headerList)
            result.insert(0, [' '])
            result.insert(0, ['table name:', tableList])
            result.insert(0, ['sql query:', sql_query])
        except:
            try:
                con.reset()
                result = retrieve_data(con, cursor, query)
                result.insert(0, [query])

            except:
                con.reset()
                result = " "
                flash('Invalid Query', 'danger')

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
    database_initialization_sequence()

    if not os.path.isfile('tables.json'):
        tables_dict = {}
        tables = get_table_list(con, cursor, 'public')
        for table in tables:
            tables_dict[table[1]] = [table[1]]
        with open('tables.json', 'w') as fp:
            json.dump(tables_dict, fp,indent=2)

    if not os.path.isfile('columns.json'):
        columns_dict = {}
        tables = get_table_list(con, cursor, 'public')
        for table in tables:
            columns_dict[table[1]] = {}
            columns = get_columns_names(con, cursor, table[1])
            for column in columns:
                columns_dict[table[1]][column] = [column]
            print(columns)
        with open('columns.json', 'w') as fp:
            json.dump(columns_dict, fp,indent=2)

    app.run(debug=True, host='0.0.0.0')
    close_db_connection(con, cursor)
