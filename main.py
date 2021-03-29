from flask import Flask, render_template, request, redirect, url_for, jsonify, json, make_response, sessions
from models.Database import db
from models.Mail import mail
from models.User import User
from models.Song import Song
from models.analysis.Filtering import Filtering
from models.analysis.AudioAnalysis import rhythmAnalysis
import lyricsgenius
import json
from FingerprintRequest import FingerprintRequest


app = Flask(__name__)
app.config['SECRET_KEY'] = 'KQ^wDan3@3aEiTEgqGUr3'  # required for session

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


@app.route('/recordingMelody', methods=['GET', 'POST'])
def melody_page():
    user = User.current_user()
    return render_template('recordingMelody.html', user=user)


@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():
    ''' This was for AudioAnalysis Testing. Remove later on
    from models.analysis import AudioAnalysis as test
    userinput = [0.001,0.712,1.458,2.168,2.876,3.529,4.29,5.007]
    custobj = test.rhythmAnalysis(userinput)
    print(custobj.onset_peak_func())
    '''
    user = User.current_user()
    return render_template('filtering.html', user=user)



def sort_results(e):
      return e['percent_match']


"""
get song lyrics using genius api
"""
def get_lyrics(songtitle, songartist):
    client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"
    genius = lyricsgenius.Genius(client_access_token)
    song = genius.search_song(title=songtitle, artist=songartist)
    lyrics = ''
    if song:
        lyrics = song.lyrics
    return lyrics


@app.route('/results', methods=['GET', 'POST'])
def result_page():
    user = User.current_user()
    #Filter the Song Results if there are any inputs from request form 
    objF = Filtering(Artist = request.form['input_artist'], Genre = request.form['input_genre'], Lyrics = request.form['input_lyrics'])
    filterResults = objF.filterRecording()# returns list of Song objects

    # Running Rhythm analysis on userTaps, includes filterResults to cross check
    objR = rhythmAnalysis(userTaps=user_result, filterResults=filterResults)
    final_res = objR.onset_peak_func()# returns list of tuples, final_results = [{<Song>, percent_match}, ... ]
    lyrics = ''
    if final_res and len(final_res) > 0:
        final_res.sort(reverse=True, key=sort_results)  # sort results by % match
        final_res = final_res[:5]  # truncate array to top 5 results
        print(final_res)
        lyrics = get_lyrics(final_res[0]['song'].title, final_res[0]['song'].artist)
        if user:
            user.add_song_log(final_res)

    # Todo: After getting results, store in user_log
    return render_template('results.html', user=user, lyrics=lyrics, filterResults=final_res)

@app.route('/melodyResults', methods=['GET', 'POST'])
def melody_result_page():
    user = User.current_user()


    result = FingerprintRequest().searchFingerprintAll(sessions['recording'])

    print(result.title)
    print(result.artists)
    print(result.score)

    print(sessions['recording'])
    lyrics = get_lyrics(result.title, result.artists)
    print(lyrics)

    return render_template('melodyResults.html', artist=result.artists, title=result.title, lyrics = lyrics, score=result.score)


@app.route('/user', methods=['GET', 'POST'])
def user_page():
    user = User.current_user()
    user_song_log = user.get_song_log()
    return render_template('userProfilePage.html', user=user, user_song_log=user_song_log)


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

def adjustArray(array):
    newArray = []
    #if invalid array, don't consider it but still return it into the userResult
    if len(array) < 3: 
        newArray = [0]
        return newArray
    dif = array[0]
    for data in array:
        num = round((data - dif), 3)
        newArray.append(num)
    return newArray
    
@app.route('/rhythm', methods=['GET', 'POST'])
def rhythmPost():
    if request.method == 'POST':
        out = receiveRhythm()
        
        global user_result
        user_result = json.loads(request.data)
        return out

@app.route('/multiplerhythm', methods=['GET', 'POST'])
def multipleRhythmPost():
    if request.method == 'POST':
        out = receiveRhythm()
        data = json.loads(request.data)
        percussionArray = []
        harmonicArray = []
        for recordedBeats in data:
            if recordedBeats['type'] == 0:
                percussionArray.append(recordedBeats['timestamp'])
            else:
                harmonicArray.append(recordedBeats['timestamp'])
        
        global user_result
        user_result = [adjustArray(percussionArray), adjustArray(harmonicArray)]
        print(user_result)
        return out

@app.route('/melody', methods=['GET', 'POST'])
def melody():
    if request.method == 'POST':

        print("Received Audio File")
        outFile = request.files["file"]
        print(outFile)
        fileName = outFile.filename
        sessions['recording'] = fileName
        print(fileName)

        outFile.save(fileName)
        print("Hoping it uploads")
        global user_result
        user_result = 0
        global melody_result
        #insert melody_result here
        #obj = melodyAnalysis(inputFile=outFile)
        #melody_result = obj.getList()
        
        melody_result = "testing"

        return jsonify(fileName)


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
    app.run(debug=True)
