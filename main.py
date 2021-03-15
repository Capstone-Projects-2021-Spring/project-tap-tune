
from flask import Flask, render_template, request
from models.Database import db
from models.Mail import mail
from models.User import User
from models.analysis.Filtering import Filtering
from models.analysis.AudioAnalysis import rhythmAnalysis
from flask_mail import Message

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ttapp'
app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
app.config['MYSQL_DB'] = 'taptune'

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'noreply.taptune@gmail.com'
app.config['MAIL_PASSWORD'] = 'kvIcIHR1r9tyLvdc&P**Q'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'noreply.taptune@gmail.com'

db.init_app(app)
mail.init_app(app)


@app.route('/')
def home_page():

    obj = rhythmAnalysis()
    obj.peak_func()

    return render_template('index.html')


@app.route('/recordingRhythm', methods=['GET', 'POST'])
def rhythm_page():
    return render_template('recordingRhythm.html')


@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():
    return render_template('filtering.html')


@app.route('/results', methods=['GET', 'POST'])
def result_page():
    #Audio Analysis

    #Filter
    obj = Filtering(Artist = request.form['input_artist'], Lyrics = request.form['input_lyrics'])
    filterResults = obj.filterRecording()

    #After getting results, store in user_log
    return render_template('results.html', artist=request.form['input_artist'], genre=request.form['input_genre'], lyrics=request.form['input_lyrics'])


@app.route('/user', methods=['GET', 'POST'])
def user_page():
    return render_template('user.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


if __name__ == '__main__':
    app.secret_key = 'KQ^wDan3@3aEiTEgqGUr3'  # required to use session
    app.run(debug=True)
