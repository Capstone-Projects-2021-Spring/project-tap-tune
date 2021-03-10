from flask import Flask, render_template, redirect, url_for, request
from models.Database import db
from models.User import User
from models.analysis.Filtering import Filtering

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ttapp'
app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
app.config['MYSQL_DB'] = 'taptune'

db.init_app(app)


@app.route('/')
def hello_world():

    # obj is used to test the filtering class
    # obj = Filtering(Artist="Queen", Genre="Rock", Lyrics="We Will Rock You")
    # obj.filterRecording()

    return render_template('index.html')
# practice page using POST and GET to send info to server
@app.route('/post', methods=["POST", "GET"])
def post_func():
    if request.method == "POST":
        value = request.form['val']
        return redirect(url_for("results", res=value))
        return
    else:
        return render_template("post.html")

# results page to redirect the POST GET page
@app.route('/<res>')
def results(res):
    return('<h1>{%s}</h1>'% res)

if __name__ == '__main__':
    app.secret_key = 'KQ^wDan3@3aEiTEgqGUr3'  # required to use session
    app.run(debug=True)
