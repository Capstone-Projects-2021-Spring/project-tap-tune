from flask import Flask, render_template, request, json, jsonify
from models.Database import db
from models.User import User
from beat_match import process_timestamp2, process_music_onset, compare

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ttapp'
app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
app.config['MYSQL_DB'] = 'taptune'

db.init_app(app)


@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/recordingRhythm', methods=['GET', 'POST'])
def rhythm_page():
    return render_template('recordingRhythm.html')

@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():
    return render_template('filtering.html')

@app.route('/results', methods=['GET', 'POST'])
def result_page():
    return render_template('results.html')

@app.route('/user', methods=['GET', 'POST'])
def user_page():
    return render_template('user.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    return render_template('login.html')


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

    stuff = []
    print('Input list: ')
    stuff.append(data)

    for i in range(len(stuff)):
        print(i)
        print(stuff[i])
    # list = [1,2,3]
    # for x in len(list):
    #     print('Input list: ')
        #print(list[x])

    # filepath = 'sampleMusic/twinkleStar.wav'
    # songName = filepath[12:-4]
    # songTimestamp = process_music_onset(filepath)
    # songP1, songP2 = process_timestamp2(songTimestamp)
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


if __name__ == '__main__':
    app.secret_key = 'KQ^wDan3@3aEiTEgqGUr3'  # required to use session
    app.run(debug=True)
