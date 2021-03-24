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

            # create song table
            create_song_table_q = """
                CREATE TABLE `song` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `title` varchar(128) NOT NULL,
                  `artist` varchar(64) NOT NULL,
                  `release_date` date DEFAULT NULL,
                  `genre` varchar(45) DEFAULT NULL,
                  `onset_hash` varchar(4096) DEFAULT NULL,
                  `peak_hash` varchar(4096) DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `title_UNIQUE` (`title`)
                )"""
            cursor.execute(create_song_table_q)
            db.connection.commit()

            # create song log table
            create_song_log_table_q = """
                CREATE TABLE `user_song_log` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `user_id` int NOT NULL,
                  `song_id` int NOT NULL,
                  `percent_match` decimal(5,4) DEFAULT NULL,
                  `result_date` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                  PRIMARY KEY (`id`),
                  KEY `fk_usl_user_id_idx` (`user_id`),
                  KEY `fk_usl_song_id_idx` (`song_id`),
                  CONSTRAINT `fk_usl_song_id` FOREIGN KEY (`song_id`) REFERENCES `song` (`id`),
                  CONSTRAINT `fk_usl_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
                )"""
            cursor.execute(create_song_log_table_q)
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
            obj = User.login(email, password)
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
            email = 'test@example.com'
            password = 'pass'
            new_password = 'newpass'
            reset_token = '123'
            reset_token_invalid = '245'
            enc_password = User._User__encrypt_password(password)  # call private method through name mangling
            cursor = get_cursor()
            cursor.execute('INSERT INTO user (username,email,`password`,reset_token) VALUES (%s,%s,%s,%s)',
                           (username, email, enc_password, reset_token))

            # check is valid token func
            r = User.is_valid_reset_token(reset_token_invalid)
            self.assertFalse(r)
            r = User.is_valid_reset_token(reset_token)
            self.assertTrue(r)

            # check if password reset is success
            r = User.reset_password(new_password, reset_token)
            self.assertTrue(r)

            # verify password reset work by logging in with new pass
            obj = User.login(email, new_password)
            self.assertIsInstance(obj, User)

    """
    test add / get song log
    """
    def test_song_log(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup user
            username = 'test'
            email = 'test@example.com'
            name = 'test name'
            password = 'pass'
            enc_password = User._User__encrypt_password(password)  # call private method through name mangling
            cursor = get_cursor()
            cursor.execute('INSERT INTO user (username,email,`name`,`password`) VALUES (%s,%s,%s,%s)',
                           (username, email, name, enc_password))
            user = User.login(email, password)
            self.assertIsInstance(user, User)

            # setup songs
            song_results = []
            song_results.append({"song_id": 1, "percent_match": 0.75, "title": "Song 1", "artist": "Artist A", "genres": "genre1"})
            song_results.append({"song_id": 2, "percent_match": 0.862, "title": "Song 2", "artist": "Artist B", "genres": "genre1, genre2"})

            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (song_results[0].get('title'), song_results[0].get('artist'), song_results[0].get('genres')))
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (song_results[1].get('title'), song_results[1].get('artist'), song_results[1].get('genres')))

            # test add log
            r = user.add_song_long(song_results)
            self.assertTrue(r)

            # test get log
            rs = user.get_song_log()
            self.assertIsNotNone(rs)



    if __name__ == '__main__':
        unittest.main()
