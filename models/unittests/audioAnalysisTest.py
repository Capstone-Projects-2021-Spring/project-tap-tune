import unittest
import flask_unittest
from flask import Flask
from models.Database import db, get_cursor
from models.Song import Song
from models.analysis.Filtering import Filtering
import models.analysis.AudioAnalysis as audioAnalysis


class UserTestCase(flask_unittest.AppClientTestCase):
    def create_app(self):
        # setup flask app for testing
        app = Flask(__name__)

        app.config['SECRET_KEY'] = 'KQ^wDan3@3aEiTEgqGUr3'  # required for session
        app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
        app.config['MYSQL_USER'] = 'ttapp'
        app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
        app.config['MYSQL_DB'] = 'taptune'

        return app

    def setUp(self, app, client):
        # Perform set up before each test, using app
        with app.app_context():
            # initialize db connection
            db.init_app(app)
        pass


if __name__ == '__main__':
    unittest.main()
