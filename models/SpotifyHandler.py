from flask import session, request
import spotipy
import uuid
import os

"""
abstracts spotipy library and methods that rely on spotify data
"""
class SpotifyHandler:

    @staticmethod
    def session_cache_path():
        cache_folder = '/tmp/'
        if request.headers['Host'] == '127.0.0.1:5000':
            cache_folder = './.spotify_cache/'
            if not os.path.exists(cache_folder):
                os.makedirs(cache_folder)

        if not session.get('spotify_cache_filename'):
            # create uuid - used as spotify cache filename
            session['spotify_cache_filename'] = str(uuid.uuid4())

        return cache_folder + session.get('spotify_cache_filename')

    @staticmethod
    def get_oauth_manager():
        redirect_url = request.headers['Host'] + '/login'
        redirect_http_header = 'https://'
        if not request.is_secure:
            redirect_http_header = 'http://'
        redirect_url = redirect_http_header + redirect_url

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=SpotifyHandler.session_cache_path())
        scope = 'playlist-read-private playlist-modify-private user-read-email user-library-read user-library-modify'
        return spotipy.oauth2.SpotifyOAuth(client_id="596f71278da94e8897cb131fb074e90c",
                                           client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386",
                                           cache_handler=cache_handler,
                                           redirect_uri=redirect_url,
                                           scope=scope)

    @staticmethod
    def clear_cache():
        fpath = SpotifyHandler.session_cache_path()
        if os.path.exists(fpath):
            os.remove(fpath)

    @staticmethod
    def is_authorized():
        am = SpotifyHandler.get_oauth_manager()
        return am.validate_token(am.get_cached_token())

