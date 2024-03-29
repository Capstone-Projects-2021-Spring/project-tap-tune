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
        app.config['SECRET_KEY'] = 'test'

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
                  `preview` varchar(255) DEFAULT NULL,
                  `onset_hash` varchar(4096) DEFAULT NULL,
                  `peak_hash` varchar(4096) DEFAULT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `song_title_artist_uidx` (`title`,`artist`)
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

            # create fingerprint table
            create_fingerprint_table_q = """
                CREATE TABLE `fingerprint` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `song_id` int NOT NULL,
                  `perc_hash` varchar(4096) DEFAULT NULL,
                  `harm_hash` varchar(4096) DEFAULT NULL,
                  `onset_hash_synced` text,
                  `peak_hash_synced` text,
                  `perc_hash_synced` text,
                  `harm_hash_synced` text,
                  `date_created` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                  `date_modified` timestamp(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `fp_song_id_uidx` (`song_id`),
                  KEY `fk_fp_song_id_idx` (`song_id`),
                  CONSTRAINT `fk_fp_song_id` FOREIGN KEY (`song_id`) REFERENCES `song` (`id`)
                )"""
            cursor.execute(create_fingerprint_table_q)
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
    test song insert into db
    """
    def test_song_insert(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            attr = dict()
            attr['genre'] = 'genre1, genre2'

            # test title required
            re = Song.insert(attr)
            self.assertTrue(re, Song.SONG_TITLE_REQUIRED)

            # test artist required
            attr['title'] = 'Song 1'
            re = Song.insert(attr)
            self.assertTrue(re, Song.SONG_ARTIST_REQUIRED)

            # test insert song
            attr['artist'] = 'Artist A'
            song = Song.insert(attr)
            self.assertIsInstance(song, Song)

            # test duplicate entry error
            re = Song.insert(attr)
            self.assertEqual(re, Song.DUPLICATE_SONG_ERROR)

    """
    test song update methods
    """
    def test_song_update(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup
            attr = dict()
            attr['title'] = 'Song 1'
            attr['artist'] = 'Artist A'
            attr['genre'] = 'genre1, genre2'
            song = Song.insert(attr)
            attr['artist'] += 'B'
            song = Song.insert(attr)

            preview = 'preview.com/example?s=va4as'
            onset_hash = 'abc1'
            peak_hash = '123x'
            perc_hash = 'fff'
            harm_hash = 'xxx'
            onset_hash_synced = 'abc1_synced'
            peak_hash_synced = '123x_synced'
            perc_hash_synced = 'fff_synced'
            harm_hash_synced = 'xxx_synced'

            # test update preview
            rpv = song.set_preview(preview)
            self.assertTrue(rpv)
            self.assertEqual(song.preview, preview)

            # test update onset hash
            ro = song.set_onset_hash(onset_hash)
            self.assertTrue(ro)
            self.assertEqual(song.onset_hash, onset_hash)

            # test update peak hash
            rp = song.set_peak_hash(peak_hash)
            self.assertTrue(rp)
            self.assertEqual(song.peak_hash, peak_hash)

            # test update percussion hash
            rpc = song.set_perc_hash(perc_hash)
            self.assertTrue(rpc)
            self.assertEqual(song.perc_hash, perc_hash)

            # test update harmonic hash
            rh = song.set_harm_hash(harm_hash)
            self.assertTrue(rh)
            self.assertEqual(song.harm_hash, harm_hash)

            # test update onset hash synced
            ro = song.set_onset_hash_synced(onset_hash_synced)
            self.assertTrue(ro)
            self.assertEqual(song.onset_hash_synced, onset_hash_synced)

            # test update peak hash synced
            rp = song.set_peak_hash_synced(peak_hash_synced)
            self.assertTrue(rp)
            self.assertEqual(song.peak_hash_synced, peak_hash_synced)

            # test update percussion hash synced
            rpc = song.set_perc_hash_synced(perc_hash_synced)
            self.assertTrue(rpc)
            self.assertEqual(song.perc_hash_synced, perc_hash_synced)

            # test update harmonic hash synced
            rh = song.set_harm_hash_synced(harm_hash_synced)
            self.assertTrue(rh)
            self.assertEqual(song.harm_hash_synced, harm_hash_synced)

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
            s = Song.insert(songs[0])
            s = Song.insert(songs[1])

            # test get all
            r = Song.get_all()
            self.assertIsNotNone(r)
            self.assertEqual(len(songs), len(r))

    """
    test get by ids
    """
    def test_song_by_ids(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # setup songs
            songs = []
            songs.append({"title": "Song 1", "artist": "Artist A", "genre": "genre1"})
            songs.append({"title": "Song 2", "artist": "Artist B", "genre": "genre1, genre2"})
            s1 = Song.insert(songs[0])
            s2 = Song.insert(songs[1])
            ids = []
            ids.append(s1.id)
            ids.append(s2.id)

            # test get by ids
            r = Song.get_by_ids(ids)
            self.assertIsNotNone(r)
            self.assertEqual(len(ids), len(r))

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
            s1 = Song.insert(songs[0])
            s2 = Song.insert(songs[1])

            # test get by artist
            r = Song.get_by_artist('b')
            self.assertIsNotNone(r)
            self.assertEqual(r[0].artist, s2.artist)

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
            s1 = Song.insert(songs[0])
            s2 = Song.insert(songs[1])

            # test get by genre
            r = Song.get_by_genre('2')
            self.assertIsNotNone(r)
            self.assertEqual(r[0].genre, s2.genre)

    if __name__ == '__main__':
        unittest.main()
