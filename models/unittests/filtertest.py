import unittest
import flask_unittest
from flask import Flask
from models.Database import db, get_cursor
from models.Song import Song
from models.analysis.Filtering import  Filtering

song1 = {
    'title': 'Pumped Up Kicks',
    'artist': 'Foster The People',
    'genre': 'indie pop, indietronica, modern rock, pop, rock',
    'release_date': '2011-05-23',
    'preview': 'https://p.scdn.co/mp3-preview/db83e69f4ef8a49f5b77e367f7031cc3bcc41b1a?cid=57483e104132413189f41cd82836d8ef',
    'onset_hash': 'B*K*J*J*J*K*9*9*9*9*9*9*J*A*8*A*8*J*K*A*8*9*9*I*K*A*8*A*8*K*J*A*9*9*9*9*9*J*A*8*A*8*J*K*A*8*J*I*K*B*7*A*8*9*9*K*9*9*A*9*9*9*J*J*A*8*J*K*A*8*9*9*J*J*A*8*A*8*J*K*A*8*A*9*8*A*J*J*A*8*J*K*A*8*9*9*I*K*A*8*A*8*J*K*9*9*A*9*9*9*J*J*A*8*J*K*A*8*I*J*9*9*K*J*B*7*K*9*9*A*8*9*A*9*9*B*7*B*7*J*B*8*A*8*A*7*J*K*C*6*A*8*A*6*0*B*7*A*9*A*9*8*A*J*B*7*A*7*K*B*8*A*8*B*6*I*0*J*A*8*9*9*I*C*8*A*8*A*8*9*A*J*A*8*B*7*J*B*8*A*8*A*7*K*J*B*7*A*8*J*B*8*A*8*A*9*8*A*A*9*I*J*K*I*.40.*J*J*.39.*.40.*K*J*A*9*A*8*I*J*J*K*J*J*J*J*.39.*A*9*8*9*L*J*K*9*9*I*J*J*K*K*I*J*J*.39.*B*S*K*J*9*A*J*.38.*J*K*.39.*J*J*K*I*A*J*9*K*J*J*J*J*B*7*J*B*8*A*8*B*6*H*2*J*J*B*7*K*A*8*A*8*A*9*9*9*J*B*6*C*7*J*B*8*A*8*A*7*J*K*I*B*8*J*K*A*8*A*9*9*9*I*K*J*J*B*8*A*8*I*K*J*A*8*9*9*J*I*0*A*8*A*9*9*9*J*A*8*A*8*J*B*8*A*8*A*8*J*J*A*8*A*8*A*8*B*8*A*8*9*A*8*A*A*9*I*J*K*I*.40.*J*J*K*I*.40.*K*J*A*9*A*8*I*J*K*J*J*J*J*J*.39.*A*J*9*K*J*K*J*I*J*K*J*K*I*J*J*K*I*B*S*K*J*9*U*.38.*K*J*.39.*J*J*K*I*A*9*9*9*A*9*J*J*J*J*A*8*K*J*A*8*J*J*J*J*A*9*A*8*J*9*A*9*9*9*9*J*A*8*J*J*K*A*9*9*8*J*J*J*9*9*K*J*A*9*9*9*J*J*J*A*8*J*B*8*A*8*J*J*J*A*8*A*8*B*8*A*8*9*A*9*9*9*9*J*A*8*J*J*K*A*9*9*8*J*J*B*7*9*9*B*8*J*A*8*A*I*B*I*J*J*K*I*.41.*J*I*.39.*K*J*K*8*A*A*K*I*S*K*J*T*A*J*I*.39.*A*I*A*9*A*J*9*A*J*I*J*K*J*.39.*J*J*V*7*.40.*K*J*A*9*J*J*J*J*J*.39.*K*I*.39.*U*9*K*T*A*J*I*K*J*J*.39.*J*J*V*7*.40.*K*J*A*9*J*J*I*K*J*.39.*K*I*.39.*U*9*K*9*9*K*',
    'peak_hash': 'B*A*L*I*K*J*J*J*J*O*E*J*S*K*A*I*T*J*A*J*T*J*A*J*J*U*I*B*S*J*A*J*R*K*B*I*I*A*J*K*J*J*F*D*K*T*B*I*I*T*A*J*J*T*J*A*E*E*J*F*E*J*T*J*A*I*T*J*A*J*H*A*K*K*J*J*E*G*I*H*A*B*J*K*R*J*B*I*K*K*I*J*J*J*L*J*J*J*J*J*K*R*C*H*J*K*J*J*J*G*C*B*I*K*J*J*E*C*C*E*C*B*I*J*K*J*J*J*I*A*B*J*J*J*J*J*M*H*K*H*J*K*J*J*I*A*A*J*I*G*D*C*I*H*T*J*A*J*J*K*H*B*J*A*K*I*N*E*A*C*H*I*T*C*H*K*I*J*K*I*A*K*J*I*J*K*C*H*I*M*Q*A*J*K*K*G*B*J*K*A*I*S*A*M*H*F*C*C*J*J*I*I*J*K*I*A*J*J*B*J*J*J*J*K*J*J*J*J*J*J*J*J*J*H*B*B*J*D*E*B*I*J*I*H*B*C*H*J*M*H*J*J*I*A*J*A*K*J*J*K*J*G*A*A*J*K*J*J*J*J*L*I*J*K*J*J*J*K*F*B*A*J*J*L*I*J*I*B*J*I*F*F*L*I*H*M*J*H*L*H*K*I*A*J*A*K*I*N*E*A*C*I*H*T*C*I*J*I*J*K*I*A*K*J*I*B*H*A*C*I*H*M*Q*A*J*K*S*K*J*A*J*J*J*J*N*H*E*C*C*J*R*I*A*J*K*I*A*K*J*A*J*J*J*J*K*J*R*B*J*J*J*J*K*I*A*J*I*B*J*J*J*J*K*J*K*G*A*A*K*I*K*I*A*J*A*I*K*J*J*K*J*R*A*J*K*J*J*K*I*A*I*A*J*K*J*J*J*K*R*B*H*A*A*J*J*J*J*A*I*A*K*J*L*B*E*F*G*J*B*F*I*A*K*I*A*K*I*B*I*I*K*G*C*B*H*A*J*B*I*J*I*J*E*F*B*I*J*I*L*E*D*C*I*H*A*J*B*H*K*I*K*I*A*J*A*K*I*K*I*M*I*I*T*B*I*I*F*D*J*A*J*A*J*J*I*B*J*L*I*J*K*J*H*K*I*K*I*A*J*A*K*I*N*E*A*C*I*I*T*B*I*J*J*I*K*J*K*.55.*.63.*',
    'harm_hash': 'B*A*5*7*7*8*2*6*4*7*G*4*5*9*2*6*9*9*8*3*6*9*2*6*4*4*2*6*9*9*9*2*F*C*8*2*6*9*8*C*G*G*5*7*9*2*6*9*J*7*C*9*9*A*8*9*A*E*4*2*6*9*9*T*B*8*2*6*9*9*B*3*C*3*I*8*8*2*6*9*2*G*C*7*2*6*9*9*9*9*A*2*B*4*2*9*8*7*C*G*B*8*4*5*8*L*G*2*7*4*7*6*9*2*6*9*2*C*3*N*6*9*5*4*8*3*5*9*F*7*7*8*2*6*C*G*K*2*6*9*L*G*3*B*7*6*9*2*6*4*4*2*G*6*D*2*G*9*E*4*A*3*9*4*4*6*3*6*7*E*2*B*A*8*3*6*9*2*6*6*5*F*8*2*B*7*3*4*4*4*0*7*2*7*4*F*B*6*6*2*3*5*9*8*B*3*4*A*3*5*9*0*0*4*0*5*6*6*8*4*5*9*2*6*9*2*6*8*2*0*C*0*4*2*7*8*6*8*9*8*4*6*0*3*D*C*6*3*5*7*2*C*5*9*I*5*6*8*4*4*7*5*6*7*5*5*9*2*6*9*2*6*7*4*7*5*F*3*2*2*6*6*6*4*D*0*4*5*2*5*5*D*5*9*9*9*3*5*A*7*7*3*3*5*8*B*5*7*5*8*4*5*9*2*6*4*4*2*6*7*5*E*B*B*0*5*8*9*C*0*8*4*B*8*4*5*9*3*5*9*8*A*A*9*9*P*N*C*6*B*6*L*I*J*A*L*6*K*.40.*J*K*A*B*6*8*7*W*7*4*6*A*7*A*A*I*J*A*L*R*8*A*K*B*8*J*9*J*9*J*J*J*A*9*J*I*J*A*K*7*B*8*S*B*J*K*9*C*Z*K*C*6*B*S*B*6*C*6*C*7*A*8*T*9*A*9*B*8*4*E*A*8*3*6*8*3*6*8*3*F*A*9*2*6*9*A*C*B*2*4*6*B*0*5*8*3*5*9*2*7*4*3*9*D*0*4*9*9*9*9*A*5*6*2*7*6*B*7*3*4*4*6*7*4*5*6*2*2*6*9*2*6*C*7*7*A*6*5*0*6*5*0*3*5*K*7*D*2*8*5*3*5*9*C*6*A*7*9*5*4*9*A*6*6*6*8*A*9*2*6*9*2*6*6*0*3*7*8*7*E*6*9*3*4*6*6*7*4*6*0*5*6*5*0*4*9*9*9*9*9*B*8*4*4*9*9*6*6*0*4*8*A*9*2*6*9*3*5*5*6*F*A*9*4*4*9*9*9*2*0*4*6*2*4*5*9*9*9*9*J*A*9*J*K*8*J*D*5*4*6*D*5*8*I*J*A*L*6*L*.39.*K*9*9*A*B*6*G*W*D*5*B*6*6*E*0*G*C*6*V*J*8*9*9*K*9*A*J*9*J*9*A*8*J*J*B*8*J*I*J*3*6*J*0*7*J*V*8*K*9*J*C*7*S*9*9*D*5*B*S*I*C*6*K*9*9*A*8*9*9*A*9*K*J*N*6*8*9*E*E*A*9*2*6*9*8*0*A*H*M*7*8*9*D*6*B*7*9*2*5*7*5*5*0*J*9*J*9*9*A*C*F*A*9*2*6*J*C*7*7*N*8*7*8*D*0*5*K*8*9*9*9*D*G*J*3*6*8*9*E*5*8*A*9*2*6*9*9*C*7*7*O*5*9*9*K*J*9*2*5*7*3*7*0*9*9*9*A*8*3*5*J*E*5*8*A*9*3*5*D*5*C*0*5*8*N*6*8*8*D*6*K*9*2*6*9*9*J*A*9*C*6*K*8*J*C*6*C*H*9*V*6*4*Y*K*9*9*K*9*A*I*B*B*6*B*6*A*J*6*5*6*B*0*4*L*J*I*B*S*A*I*9*A*3*5*B*8*9*9*9*.40.*8*J*D*5*B*6*C*3*4*I*C*H*K*8*J*.40.*K*9*9*A*J*S*J*D*5*B*6*L*J*4*6*S*I*5*4*I*9*K*9*A*8*A*9*.40.*8*J*D*5*B*6*C*8*B*7*T*K*8*K*.39.*K*9*9*A*C*6*S*J*J*B*6*L*J*B*B*6*9*L*7*8*9*9*K*9*A*.65.*',
    'perc_hash': 'B*J*J*J*J*K*9*9*A*8*A*8*K*9*8*A*8*J*K*A*9*8*9*I*K*B*8*9*8*K*J*A*9*9*9*9*9*J*A*8*B*7*J*K*A*9*9*8*I*K*B*8*9*8*9*A*J*9*9*A*9*9*9*J*A*8*A*8*J*K*A*9*8*9*J*J*B*8*9*8*K*J*A*9*A*8*9*9*J*B*7*A*8*K*J*A*8*9*9*J*J*A*9*9*5*3*8*9*6*D*9*A*9*9*9*9*J*J*A*9*J*J*A*8*B*6*K*9*9*K*J*A*8*J*A*9*A*8*9*9*A*8*B*7*B*8*J*J*A*8*B*6*J*K*C*6*A*8*B*6*0*I*B*9*9*9*9*9*J*C*6*B*7*C*6*K*A*8*B*6*D*4*0*I*0*A*7*B*7*J*K*A*9*A*8*9*9*J*B*7*B*7*K*B*7*A*8*B*7*E*4*J*C*6*A*8*J*K*A*9*A*8*8*B*9*8*A*8*A*8*B*8*J*C*6*9*9*J*J*K*I*B*9*I*9*A*9*9*A*9*A*7*B*7*B*7*K*J*B*7*9*9*J*J*K*I*A*9*9*9*A*9*9*9*9*A*A*8*9*8*J*A*9*J*J*A*8*J*J*A*9*A*7*B*9*I*9*A*9*9*A*9*A*8*9*9*I*A*8*K*B*7*A*8*J*J*K*B*6*A*9*9*9*A*9*9*9*A*8*K*B*6*B*7*K*J*A*9*A*7*J*J*B*8*B*7*J*J*A*9*A*8*9*9*J*B*7*B*8*I*K*A*8*B*7*J*8*A*C*6*A*8*K*J*A*9*9*9*9*9*9*9*9*9*J*J*K*A*9*A*6*K*J*A*9*9*8*H*2*I*0*9*9*A*8*9*9*C*7*9*8*A*8*K*J*A*9*9*8*J*J*B*8*9*8*A*7*0*C*6*A*9*9*8*0*8*A*A*7*J*J*B*8*J*J*9*9*J*J*K*I*B*9*I*K*9*9*A*9*A*8*A*8*I*K*J*B*7*9*9*J*J*K*I*A*9*9*9*A*9*9*9*9*A*A*8*A*7*B*7*A*9*J*C*6*A*8*K*I*K*I*B*9*I*9*A*9*9*A*9*A*8*A*8*9*8*A*8*K*J*A*8*K*I*K*A*7*A*9*9*9*A*9*9*A*9*9*J*B*7*A*8*J*J*A*9*9*8*J*J*K*A*8*A*8*J*A*9*A*8*9*A*J*9*9*A*7*J*K*A*9*9*8*C*6*J*C*7*8*A*B*7*J*A*9*9*9*9*A*J*9*9*9*9*J*K*9*9*9*8*J*J*A*9*9*9*A*8*J*A*9*A*8*9*A*I*A*9*9*8*J*L*9*9*9*8*J*J*B*8*8*A*A*8*J*A*9*9*9*9*A*A*7*B*7*J*C*7*D*5*J*9*A*J*I*K*9*8*B*9*A*7*K*8*B*9*L*7*A*8*I*K*D*5*J*9*A*J*I*L*H*A*J*A*9*9*B*7*A*9*A*8*I*B*8*J*J*C*6*A*9*J*I*L*9*7*B*9*I*9*A*9*A*9*9*B*7*A*8*J*J*J*J*A*9*J*I*L*H*B*8*9*9*B*8*9*A*8*A*A*8*I*K*J*J*C*6*A*9*I*J*L*9*7*B*9*I*9*A*9*A*9*9*B*7*A*8*J*J*J*J*A*9*J*I*L*H*A*9*9*9*B*8*9*A*9*9*'
}

class UserTestCase(flask_unittest.AppClientTestCase):
    # setup app for testing
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

    """
    Test for the genre filtering
    """
    def test_filtering_genre(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # checks for filtering with valid input
            obj = Filtering(Genre="pop")
            res = obj.filterGenre()
            self.assertIsInstance(res[0], Song)

            # checks for filtering without valid input
            obj = Filtering(Genre='invalid')
            res = obj.filterGenre()
            self.assertEqual(res, [])

            # checks filtering with no input
            obj = Filtering()
            res = obj.filterGenre()
            self.assertEqual(res, [])

    """
    Test for the artist filtering
    """
    def test_filtering_artist(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # checks for filtering with valid input
            obj = Filtering(Artist="AC/DC")
            res = obj.filterArtist(song_results=None)
            self.assertIsInstance(res[0], Song)

            # checks for filtering with similar valid input
            obj = Filtering(Artist="ACDC")
            res = obj.filterArtist(song_results=None)
            self.assertIsInstance(res[0], Song)

            # checks for filtering with invalid input
            obj = Filtering(Artist="invalid input")
            res = obj.filterArtist(song_results=None)
            self.assertEqual(res, [])

    """
    Test for the lyric filtering
    """
    def test_filtering_lyrics(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')

        with app.app_context():
            # test filtering with valid Lyric input
            obj = Filtering(Lyrics="We Will Rock You")
            res = obj.filterLyrics(song_results=None)
            self.assertIsInstance(res[0], Song)

            # test filtering with invalid Lyric input
            obj = Filtering(Lyrics="")
            res = obj.filterLyrics(song_results=None)
            print(res)
            self.assertEqual(res, [])
            pass

if __name__ == '__main__':
    unittest.main()

