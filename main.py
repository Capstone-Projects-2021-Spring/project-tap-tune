
from flask import Flask, render_template, request, redirect, url_for, jsonify, json, make_response
from models.Database import db
from models.Mail import mail
from models.User import User
from models.analysis.Filtering import Filtering
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
    # get logged in user or None
    user = User.current_user()
    return render_template('index.html', user=user)


@app.route('/recordingRhythm', methods=['GET', 'POST'])
def rhythm_page():
    user = User.current_user()
    return render_template('recordingRhythm.html', user=user)


@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():

    user = User.current_user()
    return render_template('filtering.html', user=user)


@app.route('/results', methods=['GET', 'POST'])
def result_page():
    user = User.current_user()

    #Audio Analysis

    #Filter
    obj = Filtering(Artist = request.form['input_artist'], Lyrics = request.form['input_lyrics'])
    filterResults = obj.filterRecording()

    #After getting results, store in user_log
    return render_template('results.html', filterResults=filterResults)

@app.route('/user', methods=['GET', 'POST'])
def user_page():
    user = User.current_user()
    return render_template('user.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # handle register form submission
    if request.method == 'POST':
        redirect_url = '/'

        # check if password and confirmation match
        if request.form['password'] == request.form['confirm_password']:
            # continue with signup
            user = User.signup(request.form['username'], request.form['email'], '', request.form['password'])

            # check signup status
            if user:
                if isinstance(user, User):
                    msg = "Signup successful."
                    category = "success"
                else:
                    category = "danger"
                    if user == User.DUPLICATE_EMAIL_ERROR:
                        msg = "Email already in use"
                    elif user == User.DUPLICATE_USERNAME_ERROR:
                        msg = "Username already taken"
                    else:
                        msg = "Signup failed."

            else:
                # will only result in this if user is None which will happen if register success but login fail
                msg = str("Error: After successful signup, could not auto sign in")
                category = "danger"
        else:
            msg = "Password and confirmation do not match"
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        # load register page
        if User.is_logged_in():
            return redirect(url_for('home_page'))
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # handle login form submission
    if request.method == 'POST':
        redirect_url = '/'
        user = User.login(request.form['email'], request.form['password'])
        if user:
            msg = "Login successful."
            category = "success"

        else:
            msg = str("Invalid Credentials")
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        # load login page
        if User.is_logged_in():
            return redirect(url_for('home_page'))
        return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    User.logout()
    return redirect(url_for('home_page'))

def receiveRhythm():
    data = request.json
    print(data)
    return jsonify(data)

@app.route('/rhythm', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        out = receiveRhythm()
        beatMatch()
    return out

def beatMatch():

    data = json.loads(request.data)

    print('WHAT DID I GET: ')
    print(data)

    print('Input list: ')
    for i in range(len(data)):
        print(data[i])



     #filepath = 'sampleMusic/twinkleStar.wav'
     #songName = filepath[12:-4]
     #songTimestamp = process_music_onset(filepath)
     #songP1, songP2 = process_timestamp2(songTimestamp)
    # userInput = receiveRhythm()
    # inputP1, inputP2 = process_timestamp2(userInput)
    # print("inputP1")
    # print(inputP1)
    #
    # # ---Decision making---
    # if compare(inputP1, songP1) == 1:
    #     print("we have a match!")
    # else:
    #     print("no match found")
	
@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

@app.route('/forgot', methods=['GET', 'POST'])
def forgotPass_page():
    return render_template('forgotPass.html')

if __name__ == '__main__':
    app.secret_key = 'KQ^wDan3@3aEiTEgqGUr3'  # required to use session
    app.run(debug=True)
