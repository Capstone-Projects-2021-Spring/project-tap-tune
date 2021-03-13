import unittest
import flask_unittest
import flask.globals
from flask import Flask
from models.Database import db, get_cursor
from models.User import User


class UserTestCase(flask_unittest.AppClientTestCase):
    """
    Create and setup flask app instance

    REQUIRED - local mysql server with specified login
    """
    def create_app(self):
        # setup flask app for testing
        app = Flask(__name__)

        app.config['TESTING'] = True
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = ''
        app.secret_key = 'test'

        return app

    """
    Setup test, runs before each test
    this is responsible for creating and necessary database structures
    """
    def setUp(self, app, client):
        # Perform set up before each test, using app
        with app.app_context():
            # initialize db connection
            db.init_app(app)

            # add test database
            cursor = get_cursor()
            cursor.execute("CREATE DATABASE testtaptune DEFAULT CHARSET 'utf8mb4'")
            db.connection.commit()

            # add db name to config
            app.config['MYSQL_DB'] = 'testtaptune'
            cursor.execute("USE testtaptune")

            # create user table
            create_user_table_q = """
                CREATE TABLE `user` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `username` varchar(45) NOT NULL,
                  `email` varchar(256) NOT NULL,
                  `name` varchar(64) DEFAULT NULL,
                  `password` varchar(128) DEFAULT NULL,
                  `reset_token` varchar(64) DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `user_username_uidx` (`username`),
                  UNIQUE KEY `user_email_uidx` (`email`)
                )"""
            cursor.execute(create_user_table_q)
            db.connection.commit()
        pass

    """
    Teardown test, runs after each test
    this is responsible for removing all database structures
    """
    def tearDown(self, app, client):
        # Perform tear down after each test, using app
        # Remove test database
        with app.app_context():
            cursor = get_cursor()
            cursor.execute("DROP DATABASE testtaptune")
            db.connection.commit()
        pass

    """
    Test signup method
    """
    def test_signup(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            username = 'test'
            email = 'test@example.com'
            name = 'test name'
            password = 'pass'

            # test signup
            obj = User.signup(username, email, name, password)
            self.assertIsInstance(obj, User)
            self.assertEqual(username, obj.username)
            self.assertEqual(email, obj.email)
            self.assertEqual(name, obj.name)

    """
    test login method
    """
    def test_user_login(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            user_id = 1
            username = 'test'
            email = 'test@example.com'
            name = 'test name'
            password = 'pass'
            enc_password = User._User__encrypt_password(password)  # call private method through name mangling
            cursor = get_cursor()
            cursor.execute('INSERT INTO user (username,email,`name`,`password`) VALUES (%s,%s,%s,%s)',
                           (username, email, name, enc_password))

            # test login
            obj = User.login('test', 'pass')
            self.assertIsInstance(obj, User)
            self.assertEqual(username, obj.username)
            self.assertEqual(email, obj.email)
            self.assertEqual(name, obj.name)

            # test session is set
            self.assertEqual(user_id, flask.globals.session['user_id'])
            self.assertEqual(username, flask.globals.session['username'])
            self.assertEqual(email, flask.globals.session['email'])
            self.assertEqual(name, flask.globals.session['name'])

    """
    test logout method
    """
    def test_user_logout(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            flask.globals.session['username'] = 'test'
            flask.globals.session['email'] = 'test@example.com'
            flask.globals.session['name'] = 'testname'

            # test logout cleared session
            User.logout()
            self.assertNotIn('user_id', flask.globals.session)
            self.assertNotIn('username', flask.globals.session)
            self.assertNotIn('name', flask.globals.session)
            self.assertNotIn('email', flask.globals.session)

    """
    test reset password functionality
    """
    def test_reset_password(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            username = 'test'
            password = 'pass'
            new_password = 'newpass'
            reset_token = '123'
            reset_token_invalid = '245'
            enc_password = User._User__encrypt_password(password)  # call private method through name mangling
            cursor = get_cursor()
            cursor.execute('INSERT INTO user (username,email,`password`,reset_token) VALUES (%s,%s,%s,%s)',
                           (username, 'test@example.com', enc_password, reset_token))

            # check is valid token func
            r = User.is_valid_reset_token(reset_token_invalid)
            self.assertFalse(r)
            r = User.is_valid_reset_token(reset_token)
            self.assertTrue(r)

            # check if password reset is success
            r = User.reset_password(new_password, reset_token)
            self.assertTrue(r)

            # verify password reset work by logging in with new pass
            obj = User.login('test', new_password)
            self.assertIsInstance(obj, User)

    if __name__ == '__main__':
        unittest.main()
