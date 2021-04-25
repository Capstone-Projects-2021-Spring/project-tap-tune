"""
Use Case #1:
Accesses Tap Tune website
Uses Tap (keyboard) function to record rhythm
Uses the Artist filter in his search
Gets a song suggestion

def test_usecase1(self):
    Set timestamp array for input
        [user_result = *timestamp array*]
    Use artist filter get result
        [filterResults = objF = Filtering(Artist=*some artist)]
    Send timestamp array and filter result to analysis
        objR = rhythmAnalysis(userTaps=user_result, filterResults=filterResults)
    Get song suggestion with analysis results as track seeds
        parse objR for song title and artist
        Search Spotify of song ids
        Use spotify suggest request and get result
"""
import unittest
import flask_unittest
from flask import Flask
from models.Database import db, get_cursor
from models.Song import Song
from models.analysis.Filtering import Filtering
from models.analysis.AudioAnalysis import rhythmAnalysis
from models.SpotifyHandler import SpotifyHandler
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import requests

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
    Integration test for Use Case 1
    """
    def test_integration_1(self, app, client):
        # mock client request to setup session use
        rv = client.get('/')
        with app.app_context():
            artist = "Adele"
            userResult = [[0], [0.702,1.374,2.04,2.685,3.327,4.423,5.096,5.758,6.717,7.648,8.67,9.255,9.794,10.776,11.318,11.867,13.217,13.956,14.76,15.247]]
            # first test for the correct filtering output
            objF = Filtering(Artist=artist)
            filterResults = objF.filterRecording()
            self.assertIsInstance(filterResults[0], Song)

            # second test for correct analysis output
            objR = rhythmAnalysis(userTaps=userResult, filterResults=filterResults)
            final_res = objR.onset_peak_func()
            self.assertIsInstance(final_res[0]['song'], Song)

            """
            START SPOTIFY SUGGESTION TESTING
            """
            # getting credentials set up
            spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                            client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))
            CLIENT_ID = '57483e104132413189f41cd82836d8ef'
            CLIENT_SECRET = '2bcd745069bd4602ae77d1a348c0f2fe'

            AUTH_URL = 'https://accounts.spotify.com/api/token'

            # POST
            auth_response = requests.post(AUTH_URL, {
                'grant_type': 'client_credentials',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
            })

            # convert the response to JSON
            auth_response_data = auth_response.json()

            # save the access token
            access_token = auth_response_data['access_token']

            headers = {
                'Authorization': 'Bearer {token}'.format(token=access_token)
            }

            # base URL of all Spotify API endpoints
            REC_ENDPOINT = 'https://api.spotify.com/v1/recommendations'

            # get the track id
            title = final_res[0]['song'].title
            track_ids = []
            searchResults = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
            # print(searchResults)
            if searchResults and searchResults["tracks"]["total"] > 0:
                track_id = searchResults['tracks']['items'][0]["id"]
                track_ids.append(track_id)

            # request for a song suggestion
            r = requests.get(REC_ENDPOINT + '/', headers=headers,
                             params={'seed_artist': None,
                                     'seed_genres': None,
                                     'seed_tracks': track_ids,
                                     'target_acousticness': None,
                                     'target_danceability': None,
                                     'target_energy': None,
                                     'target_instrumentalness': None,
                                     'target_loudness': None
                                     })
            recommendations = r.json()

            # third test to check valid suggestion output
            self.assertIsNotNone(recommendations)

if __name__ == '__main__':
    unittest.main()
