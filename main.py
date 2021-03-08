from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ttapp'
app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
app.config['MYSQL_DB'] = 'taptune'

mysql = MySQL(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/#recordingRhythm')
def rhythm_page():
    return render_template('recordingRhythm.html')

@app.route('/#filter')
def filter_page():
    return render_template('filtering.html')

@app.route('/#results')
def result_page():
    return render_template('results.html')


if __name__ == '__main__':
    app.run(debug=True)
