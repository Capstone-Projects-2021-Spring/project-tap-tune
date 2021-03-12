from flask import Flask, render_template, request, json
flask_test  = Flask(__name__)

@flask_test.route('/')
def fun1():
    return "this is back end"

@flask_test.route('/recordingRhythm')