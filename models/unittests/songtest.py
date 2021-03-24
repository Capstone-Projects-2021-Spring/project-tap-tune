import unittest
import flask_unittest
import flask.globals
from flask import Flask
from models.Database import db, get_cursor
from models.Song import Song


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
    test get all
    """
    def test_song_all(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup songs
            songs = []
            songs.append({"title": "Song 1", "artist": "Artist A", "genre": "genre1"})
            songs.append({"title": "Song 2", "artist": "Artist B", "genre": "genre1, genre2"})

            cursor = get_cursor()
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[0].get('title'), songs[0].get('artist'), songs[0].get('genre')))
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[1].get('title'), songs[1].get('artist'), songs[1].get('genre')))

            # test get all
            r = Song.get_all()
            self.assertIsNotNone(r)

    """
    test get by artist
    """
    def test_song_by_artist(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup songs
            songs = []
            songs.append({"title": "Song 1", "artist": "Artist A", "genre": "genre1"})
            songs.append({"title": "Song 2", "artist": "Artist B", "genre": "genre1, genre2"})

            cursor = get_cursor()
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[0].get('title'), songs[0].get('artist'), songs[0].get('genre')))
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[1].get('title'), songs[1].get('artist'), songs[1].get('genre')))

            # test get all
            r = Song.get_by_artist('b')
            self.assertIsNotNone(r)
            self.assertEqual(r[0].artist, 'Artist B')

    """
    test get by genre
    """
    def test_song_by_genre(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup songs
            songs = []
            songs.append({"title": "Song 1", "artist": "Artist A", "genre": "genre1"})
            songs.append({"title": "Song 2", "artist": "Artist B", "genre": "genre1, genre2"})

            cursor = get_cursor()
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[0].get('title'), songs[0].get('artist'), songs[0].get('genre')))
            cursor.execute('INSERT INTO song (title,artist,genre) VALUES (%s,%s,%s)',
                           (songs[1].get('title'), songs[1].get('artist'), songs[1].get('genre')))

            # test get all
            r = Song.get_by_genre('2')
            self.assertIsNotNone(r)
            self.assertEqual(r[0].genre, "genre1, genre2")

    if __name__ == '__main__':
        unittest.main()
