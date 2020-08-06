import time, os
from flask import Flask, render_template, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import csv


DBUSER = 'admin'
DBPASS = 'supersecretpwd'
DBHOST = 'db'
DBPORT = '5432'
DBNAME = 'testdb'


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
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    age = db.Column(db.Integer())

    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age


def database_initialization_sequence():
    db.create_all()
    with open('data/dummy_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.session.add(students(row['Name'], row['City'], row['Age']))        

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

        return render_template('query_data.html')


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
    database_initialization_sequence()
    app.run(debug=True, host='0.0.0.0')
