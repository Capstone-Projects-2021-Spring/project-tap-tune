from flask import Flask, render_template, request, redirect, url_for, jsonify, json, make_response
from models.Database import db
from models.Mail import mail
from models.User import User
from models.analysis.Filtering import Filtering
from models.analysis.AudioAnalysis import rhythmAnalysis
from flask_mail import Message

import json
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
    return render_template('recordingRhythm.html')

@app.route('/recordingMelody', methods=['GET', 'POST'])
def melody_page():
    return render_template('recordingMelody.html')

@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():
    user = User.current_user()
    return render_template('filtering.html', user=user)


@app.route('/results', methods=['GET', 'POST'])
def result_page():
    user = User.current_user()

    #Filter the Song Results if there are any inputs from request form 
    obj = Filtering(Artist = request.form['input_artist'], Genre = request.form['input_genre'], Lyrics = request.form['input_lyrics'])
    print(user_result)
    filterResults = obj.filterRecording(user_result)
    
    #Todo: After getting results, store in user_log 
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

    data = json.loads(request.data)
    obj = rhythmAnalysis(userTaps=data)

    global user_result
    user_result = obj.onset_peak_func()
    return out

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'POST':
        # handle request
        rval = User.send_reset_password_email(request.form['email'])
        if rval:
            msg = "An email was sent with instructions to reset your password."
            category = "success"

        else:
            msg = str("Email not sent")
            category = "danger"

        resp = {'feedback': msg, 'category': category}
        return make_response(jsonify(resp), 200)
    else:
        return render_template('forgotPass.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_pass():
    if request.method == 'POST':
        redirect_url = '/login'

        # check if valid reset token
        # its already checked in page load but can be issue if multiple forms were opened
        if User.is_valid_reset_token(request.form['token']):
            # check if password and confirmation match
            if request.form['password'] == request.form['confirm_password']:
                # continue with reset
                reset = User.reset_password(request.form['password'], request.form['token'])

                # check reset status
                if reset:
                    msg = "Password Reset!"
                    category = "success"
                else:
                    msg = "Password reset failed"
                    category = "danger"
            else:
                msg = "Password and confirmation do not match"
                category = "danger"
        else:
            msg = "Password reset failed. Invalid link."
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        token = request.args.get('token')
        print(token)
        is_valid_token = False
        if token:
            is_valid_token = User.is_valid_reset_token(token)

        return render_template('resetPass.html', is_valid_token=is_valid_token, token=token)


if __name__ == '__main__':
    app.secret_key = 'KQ^wDan3@3aEiTEgqGUr3'  # required to use session
    app.run(debug=True)
