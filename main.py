from flask import Flask, render_template, request, redirect, url_for, jsonify, json, make_response, session
from models.Database import db
from models.Mail import mail
from models.User import User
from models.Source import Source
from models.Song import Song
from models.analysis.Filtering import Filtering
from models.analysis.AudioAnalysis import rhythmAnalysis
from yt_sp_autosource_POC import AutoSource
import lyricsgenius
import json
import time
import csv
import requests
import random
from FingerprintRequest import FingerprintRequest, foundsong
import speech_recognition

from update_db_songs import update_songs_sync_hash
from models.SpotifyHandler import SpotifyHandler
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KQ^wDan3@3aEiTEgqGUr3'  # required for session

app.config['MYSQL_HOST'] = 'taptune.cqo4soz29he6.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'ttapp'
app.config['MYSQL_PASSWORD'] = '7tV9qEMc3!3Bp8M$zBSt9'
app.config['MYSQL_DB'] = 'taptune'

# configuration of mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'noreply.taptune@gmail.com'
app.config['MAIL_PASSWORD'] = 'kvIcIHR1r9tyLvdc&P**Q'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'noreply.taptune@gmail.com'

db.init_app(app)
mail.init_app(app)


@app.route('/')
def home_page():
    # get logged in user or None
    user = User.current_user()
    # print(request.headers['Host'])
    # print(session)
    return render_template('index.html', user=user)


@app.route('/update-songs')
def update_songs():
    update_songs_sync_hash()
    return render_template('index.html')


@app.route('/recordingRhythm', methods=['GET', 'POST'])
def rhythm_page():
    user = User.current_user()
    return render_template('recordingRhythm.html', user=user)


@app.route('/about', methods=['GET', 'POST'])
def about_page():
    user = User.current_user()
    r = make_response(render_template('about.html', user=user))
    r.headers.set('Content-Security-Policy', "frame-ancestors 'self' https://open.spotify.com")
    return r


@app.route('/recordingMelody', methods=['GET', 'POST'])
def melody_page():
    user = User.current_user()
    return render_template('recordingMelody.html', user=user)


@app.route('/filtering', methods=['GET', 'POST'])
def filter_page():
    ''' This was for AudioAnalysis Testing. Remove later on
    from models.analysis import AudioAnalysis as test
    userinput = [0.001,0.712,1.458,2.168,2.876,3.529,4.29,5.007]
    custobj = test.rhythmAnalysis(userinput)
    print(custobj.onset_peak_func())
    '''
    user = User.current_user()
    return render_template('filtering.html', user=user)


def sort_results(e):
    return e['percent_match']


"""
get song lyrics using genius api
"""


def get_lyrics(songtitle, songartist):
    client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"
    genius = lyricsgenius.Genius(client_access_token)
    song = genius.search_song(title=songtitle, artist=songartist)
    lyrics = 'Not Found'
    if song:
        lyrics = song.lyrics
    return lyrics


def get_photo(songtitle, songartist):
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                    client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))

    photo = ''
    # For each title and artist, find track id
    searchResults = spotify.search(q="artist:" + songartist + " track:" + songtitle, type="track", limit=1)
    print(searchResults)
    if searchResults and searchResults["tracks"]["total"] > 0:
        photo = searchResults["tracks"]["items"][0]["album"]["images"][1]

    return photo


@app.route('/results', methods=['GET', 'POST'])
def result_page():
    user = User.current_user()
    # Filter the Song Results if there are any inputs from request form
    objF = Filtering(Artist=request.form['input_artist'], Genre=request.form['input_genre'],
                     Lyrics=request.form['input_lyrics'])
    filterResults = objF.filterRecording()  # returns list of Song objects
    print(filterResults)
    user_result = session['user_result']
    # Running Rhythm analysis on userTaps, includes filterResults to cross check
    objR = rhythmAnalysis(userTaps=user_result, filterResults=filterResults)
    if objR.input_type == 0:
        userRecordingType = "General"
        final_res = objR.onset_peak_func()  # returns list of tuples, final_results = [{<Song>, percent_match, matched_pattern}, ... ]
    if objR.input_type == 1:
        userRecordingType = "Percussion"
        final_res = objR.onset_peak_fun_percussive()
    if objR.input_type == 2:
        userRecordingType = "Harmonic"
        final_res = objR.onset_peak_func_harmonic()

    lyrics = ''
    photo = ''
    spotifyTimestamp = ''
    spotify_data = None
    print("----------------")
    # final_res[0]['matched_pattern'] = list(final_res[0]['matched_pattern'])
    # print(type(final_res[0]))
    # print(final_res[0]['matched_pattern'])
    print("----------------")
    if final_res and len(final_res) > 0:
        final_res.sort(reverse=True, key=sort_results)  # sort results by % match
        final_res = final_res[:10]  # truncate array to top 10 results
        spotify_data = spotify_embeds(final_res[0]['song'].title, final_res[0]['song'].artist)
        lyrics = get_lyrics(final_res[0]['song'].title, final_res[0]['song'].artist)
        spotifyTimestamp = final_res[0]['start_time']
        #photo = get_photo(final_res[0]['song'].title, final_res[0]['song'].artist)
        if user:
            user.add_song_log(final_res)
    userTapCount = len(user_result[1])
    # Todo: After getting results, store in user_log
    r = make_response(
        render_template('results.html', userTaps=user_result[1], user=user, lyrics=lyrics, filterResults=final_res,
                        userTapCount=userTapCount, userRecordingType=userRecordingType,
                        spotifyTimestamp=spotifyTimestamp,
                        spotify_data=spotify_data))
    r.headers.set('Content-Security-Policy', "frame-ancestors 'self' https://open.spotify.com")
    return r


def getMelPreview(title, artist):
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                    client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))
    trackURI = ''
    # Parse Tracks in data to find track id
    searchResults = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
    if searchResults and searchResults["tracks"]["total"] > 0:
        trackURI = searchResults["tracks"]['items'][0]["uri"]

        splitURI = trackURI.split(':')
        print(splitURI)
        return splitURI[2]


@app.route('/melodyResults', methods=['GET', 'POST'])
def melody_result_page():
    user = User.current_user()

    melList = ''
    melTitle = ''
    melArtist = ''
    melScore = ''
    photo = ''
    melURL = ''

    try:
        recording_filename = session.get('recording')
        result = foundsong()  # initialize to empty class, to fail gracefully
        lyrics = ''
        if recording_filename:
            print("[[[[[[[[[[[[[")
            print("SESSION FILENAME = ", recording_filename)
            print("[[[[[[[[[[[[[")

            with speech_recognition.AudioFile(recording_filename) as source:  # Load the file
                r = speech_recognition.Recognizer()
                r.energy_threshold = 4000
                r.dynamic_energy_threshold = True
                data = r.record(source)
                # Google Speech API Key
                try:
                    lyricsFromFile = r.recognize_google(data, key='AIzaSyAEi5c2CU_gf3RsJGv6UVt1EqnylEn6mvc')
                except:
                    lyricsFromFile = ''
                    pass
                result = FingerprintRequest().searchFingerprintAll(recording_filename, lyricsFromFile)
                pass

            if result.title == 'None' and result.artists == 'None' and result.score == 'None':
                print("There are none values")
            else:
                melTitle = result.title
                melArtist = result.artists
                melScore = result.score
                print("There is stuff")

            print(result.title)
            print(result.artists)
            print(result.score)
            lyrics = get_lyrics(result.title, result.artists)
            # photo  = get_photo(result.title, result.artists)
            #print(lyrics)

            getPreview = str(getMelPreview(result.title, result.artists))
            if(getPreview == 'None'):
                melURL = ''
                print(getPreview)
            else:
                melURL = "https://open.spotify.com/embed/track/" + getMelPreview(result.title, result.artists)
                print(melURL)

            print("STUFFY NOODLES")
            melList = FingerprintRequest().getHummingFingerprint(session.get('recording'))
        else:
            print('recording file not found in session')

    except Exception as e:
        print(e)
        result = foundsong()  # initialize to empty class, to fail gracefully
        lyrics = ''

    return render_template('melodyResults.html', user=user, artist=melArtist, title=melTitle, lyrics=lyrics,
                           score=melScore, melResults=melList, melPreview=melURL)


@app.route('/user', methods=['GET', 'POST'])
def user_page():
    phrases = ["Hey There,", "Hello,", "What's Up?", "Good To See You,", "Greetings,", "Salutations,", "Howdy,", "Hey,",
               "Nice To See You,"]
    rand = random.randint(0, 8)
    user = User.current_user()
    user_song_log = user.get_song_log()
    user_fav_songs = user.get_favorite_songs()
    r = make_response(render_template('userProfilePage.html', user=user, user_fav_songs=user_fav_songs,
                                      user_song_log=user_song_log, phrases=phrases, rand=rand))
    r.headers.set('Content-Security-Policy', "frame-ancestors 'self' https://open.spotify.com")
    return r
    # return render_template('userProfilePage.html', user=user, user_fav_songs=user_fav_songs, user_song_log=user_song_log)


@app.route('/add-user-fav-song', methods=['GET', 'POST'])
def add_user_fav_song():
    user = User.current_user()
    song_id = request.form['song_id']
    r = user.add_favorite_song(song_id)
    if r == User.DUPLICATE_FAVORITE_SONG_ERROR or r == User.UNKNOWN_ERROR:
        msg = r
        category = "danger"
    else:
        msg = "Song added to favorites."
        category = "success"

    resp = {'feedback': msg, 'category': category}
    return make_response(jsonify(resp), 200)


@app.route('/add-user-log-spotify', methods=['GET', 'POST'])
def add_user_log_spotify():
    user = User.current_user()

    try:
        data = json.loads(request.data)
        print(data)

        msg = ""
        if User.is_spotify_login():
            # Integration for Adding to Spotify User Playlist based on track title and artist
            am = SpotifyHandler.get_oauth_manager()
            spotify = spotipy.Spotify(auth_manager=am)
            sp_user = spotify.me()
            username = sp_user["id"]

            # Using title and artist, find track id
            track_id = "not found"
            track_ids = []
            search_results = spotify.search(q="artist:" + data[1] + " track:" + data[0], type="track", limit=1)
            print(search_results)
            if search_results and search_results["tracks"]["total"] > 0:
                track_id = search_results['tracks']['items'][0]["id"]
                track_ids.append(track_id)

            # Find Playlist and Add track
            if track_id != "not found":
                # get playlists from spotify
                playlists = spotify.current_user_playlists()
                print(playlists)

                tt_playlist = None

                # find TapTune playlist
                for playlist in playlists.get('items'):
                    if playlist.get('name') == "TapTune":
                        tt_playlist = playlist
                        break

                if not tt_playlist:
                    # add spotify playlist
                    tt_playlist = spotify.user_playlist_create(username, "TapTune", public=False)

                print(tt_playlist)
                if tt_playlist:
                    # remove track from spotify playlist
                    # doing it this way because the only way to check if a track is in a playlist is to
                    # loop through all tracks in the playlist (there could be hundreds)
                    # this is faster and simpler
                    spotify.playlist_remove_all_occurrences_of_items(tt_playlist.get('id'), track_ids)

                    # add track to spotify playlist
                    results = spotify.playlist_add_items(tt_playlist.get('id'), track_ids)
                    print(results)
                    if results:
                        msg = "Song added to Spotify playlist - [TapTune]."
                        category = "success"
                    else:
                        msg = "Song could not be added to Spotify playlist - [TapTune]"
                        category = "danger"
                else:
                    msg = "Playlist TapTune could not be created on Spotify"
                    category = "danger"
            else:
                msg = "Song could not be found on Spotify based on title and artist"
                category = "danger"
        else:
            category = "success"

        # add to favorites in TapTune database
        if category != "danger":
            if msg != "":
                msg += "<br>"

            song_id = data[2]
            r = user.add_favorite_song(song_id)
            if r == User.DUPLICATE_FAVORITE_SONG_ERROR or r == User.UNKNOWN_ERROR:
                msg += r
                category = "danger"
            else:
                msg += "Song added to favorites."
                category = "success"

    except Exception as e:
        print(e)
        msg = "Could not add song to Spotify playlist"
        category = "danger"

    resp = {'feedback': msg, 'category': category}
    return make_response(jsonify(resp), 200)


@app.route('/remove-user-fav-spotify', methods=['GET', 'POST'])
def remove_user_fav_spotify():
    user = User.current_user()

    data = json.loads(request.data)
    print(data)

    #Delete the favorite from user
    songid = data[2]
    r = user.delete_favorite_song(songid)
    if r == User.DUPLICATE_FAVORITE_SONG_ERROR or r == User.UNKNOWN_ERROR:
        msg = r
        category = "danger"
    else:
        msg = "Song deleted from favorites."
        category = "success"

    try:
        #Remove from Spotify Playlist if Spotify User
        if User.is_spotify_login():
            # Integration for Adding to Spotify User Playlist based on track title and artist
            am = SpotifyHandler.get_oauth_manager()
            spotify = spotipy.Spotify(auth_manager=am)
            sp_user = spotify.me()
            username = sp_user["id"]

            # Using title and artist, find all track ids to a list
            track_id = "not found"
            track_ids= []
            title = data[0]
            artist = data[1]
            search_results = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
            print(search_results)
            if search_results and search_results["tracks"]["total"] > 0:
                track_id = search_results['tracks']['items'][0]["uri"]
                track_ids.append(track_id)
                print(track_id)

            # Find Playlist and Remove track
            if track_id != "not found":
                # get playlists from spotify
                playlists = spotify.current_user_playlists()
                tt_playlist = None

                # find TapTune playlist
                for playlist in playlists.get('items'):
                    if playlist.get('name') == "TapTune":
                        tt_playlist = playlist
                        break

                if not tt_playlist:
                    # add spotify playlist
                    msg += "<br>Spotify playlist doesn't exist"
                    resp = {'feedback': msg, 'category': "danger"}
                    return make_response(jsonify(resp), 200)

                print(tt_playlist)
                if tt_playlist:
                    # remove track from spotify playlist
                    spotify.playlist_remove_all_occurrences_of_items(tt_playlist.get('id'), track_ids)
                    msg += "<br>Song removed from Spotify playlist - [TapTune]."
                    category = "success"
                else:
                    msg += "<br>Spotify playlist doesn't exist"
                    resp = {'feedback': msg, 'category': "danger"}
                    return make_response(jsonify(resp), 200)
            else:
                msg += "<br>Song could not be found on Spotify"
                category = "danger"  

    except Exception as e:
        print(e)
        msg += "<br>Could not remove song from Spotify playlist"
        category = "danger"

    resp = {'feedback': msg, 'category': category}
    return make_response(jsonify(resp), 200)


@app.route('/remove-user-song-history', methods=['GET', 'POST'])
def remove_user_song_history():
    user = User.current_user()

    try:
        data = json.loads(request.data)
        print(data)

        msg = ""
        category = "success"

        songID = data[0]

            # song_id = request.form['song_id']
        r = user.delete_history_song(songID)
        if r == User.UNKNOWN_ERROR:
            msg = r
            category = "danger"
        else:
            msg = "Song deleted from history."
            category = "success"

    except Exception as e:
        print(e)
        msg = "Could not remove song from User History"
        category = "danger"

    resp = {'feedback': msg, 'category': category}
    return make_response(jsonify(resp), 200)


@app.route('/spotify-suggest', methods=['GET', 'POST'])
def spotify_suggest():
    if request.method == 'POST':
        # Getting song suggestion based on spotify API
        data = json.loads(request.data)
        input_tracks = data[0]
        attributes = data[1]
        print(attributes)

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

        # Parse Slider information
        # Define Initial Target_Values [Acousticness, Danceability, Energy Instrumentalness, Loudness]
        target_values = [None, None, None, None, None]
        for index, item in enumerate(attributes):
            if item:
                target_values[index] = item
        print(target_values)

        # Parse Tracks in data to find track ids
        # For each title and artist, find track id
        track_ids = []
        for items in input_tracks:
            """
            INCLUDE PARSING OF SLIDER INFORMATION
            """
            split = items.split(',')
            title = split[0]
            artist = split[1]
            print(title + artist)
            searchResults = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
            # print(searchResults)
            if searchResults and searchResults["tracks"]["total"] > 0:
                track_id = searchResults['tracks']['items'][0]["id"]
                track_ids.append(track_id)
                # print(searchResults['tracks']['items'][0])

        # Using Track Ids, get a recommended song through Spotify API
        if (len(track_ids) > 0):
            # recommendations = spotify.recommendations(seed_artists=None, seed_genres=None, seed_tracks=track_ids, limit=1)
            # actual GET request with proper header
            r = requests.get(REC_ENDPOINT + '/', headers=headers,
                             params={'seed_artist': None,
                                     'seed_genres': None,
                                     'seed_tracks': track_ids,
                                     'target_acousticness': target_values[0],
                                     'target_danceability': target_values[1],
                                     'target_energy': target_values[2],
                                     'target_instrumentalness': target_values[3],
                                     'target_loudness': target_values[4]
                                     })
            print(target_values)
            recommendations = r.json()
            if recommendations:
                print(recommendations)
                recommendedTitle = recommendations["tracks"][0]["name"]
                recommendedArtist = recommendations["tracks"][0]["artists"][0]["name"]
                recommendedSongImage = recommendations["tracks"][0]["album"]["images"][1]
                recommendedSongLink = recommendations["tracks"][0]["external_urls"]["spotify"]
                msg = "Song suggested by related tracks."
                data = [recommendedTitle, recommendedArtist, recommendedSongImage, recommendedSongLink]
                category = "success"

            else:
                msg = "Song could not be suggested, no found tracks in input array."
                data = "None"
                category = "warning"

        else:
            msg = "Song could not be suggested, no found tracks in input array."
            data = "None"
            category = "warning"

        resp = {'feedback': msg, 'category': category, 'data': data}
        return make_response(jsonify(resp), 200)

@app.route('/spotify-source', methods=['GET', 'POST'])
def spotify_source():
    if request.method == 'POST':
        data = json.loads(request.data)
        recommendedTitle = data[0]
        recommendedArtist = data[1]
        obj = AutoSource(title=recommendedTitle, artist=recommendedArtist)
        obj.process_info()

        if obj :
            resp = {'feedback': "Success"}
            return make_response(jsonify(resp), 200)
        else :
            resp = {'feedback': "failure"}
            print("failed to AutoSource from spotify recommendedTitle and artist")
            return make_response(jsonify(resp), 200)

@app.route('/spotify-track-metadata', methods=['GET', 'POST'])
def spotify_track_metadata():
    if request.method == 'POST':
        spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                        client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))
        # Getting song suggestion based on spotify API
        data = json.loads(request.data)
        title = data[0]
        artist = data[1]

        # Parse Tracks in data to find track id
        lyrics = ''
        searchResults = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
        lyrics = get_lyrics(title, artist)
        if searchResults and searchResults["tracks"]["total"] > 0:
            trackLink = searchResults['tracks']['items'][0]["external_urls"]["spotify"]
            trackURI = searchResults["tracks"]['items'][0]["uri"]
            trackAlbumImage = searchResults["tracks"]['items'][0]["album"]["images"][0]

            resp_data = [trackLink, trackURI, lyrics, trackAlbumImage]
            msg = "Song found, returning links."
            category = "success"
        else:
            msg = "Song could not be found in spotify API"
            resp_data = ['', '', lyrics, '']
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'data': resp_data}
        return make_response(jsonify(resp), 200)


def spotify_embeds(title, artist):
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                    client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))

    # Parse Tracks in data to find track id
    lyrics = ''
    searchResults = spotify.search(q="artist:" + artist + " track:" + title, type="track", limit=1)
    resp_data = ['', '', 'https://www.dia.org/sites/default/files/No_Img_Avail.jpg']
    if searchResults and searchResults["tracks"]["total"] > 0:
        spotifyHead = "https://open.spotify.com/"
        spotify = searchResults['tracks']['items'][0]["external_urls"]["spotify"]
        spotifyTail = spotify[len(spotifyHead):len(spotify)]

        trackLink = spotifyHead + "embed/" + spotifyTail
        trackURI = searchResults["tracks"]['items'][0]["uri"]
        trackAlbumImage = searchResults["tracks"]['items'][0]["album"]["images"][0]
        resp_data = [trackLink, trackURI, trackAlbumImage]
    return resp_data


@app.route('/register', methods=['GET', 'POST'])
def register():
    # handle register form submission
    if request.method == 'POST':
        redirect_url = '/'

        # check if password and confirmation match
        if request.form['password'] == request.form['confirm_password']:
            # continue with signup
            user = User.signup(request.form['username'], request.form['email'], '', request.form['password'])

            # check signup status
            if user:
                if isinstance(user, User):
                    msg = "Signup successful."
                    category = "success"
                else:
                    category = "danger"
                    if user == User.DUPLICATE_EMAIL_ERROR:
                        msg = "Email already in use"
                    elif user == User.DUPLICATE_USERNAME_ERROR:
                        msg = "Username already taken"
                    else:
                        msg = "Signup failed."

            else:
                # will only result in this if user is None which will happen if register success but login fail
                msg = str("Error: After successful signup, could not auto sign in")
                category = "danger"
        else:
            msg = "Password and confirmation do not match"
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        # load register page
        if User.is_logged_in():
            return redirect(url_for('home_page'))
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # handle login form submission
    if request.method == 'POST':
        redirect_url = '/'
        user = User.login(request.form['email'], request.form['password'])
        if user:
            msg = "Login successful."
            category = "success"

        else:
            msg = str("Invalid Credentials")
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        # redirect to home page if user logged in
        if User.is_logged_in():
            return redirect(url_for('home_page'))

        # handle spotify login
        am = SpotifyHandler.get_oauth_manager()
        spotify_login_url = ''
        spotify_error = ''

        # handle successful spotify login
        if request.args.get("code"):
            try:
                am.get_access_token(request.args.get("code"))
                spotify = spotipy.Spotify(auth_manager=am)
                sp_user = spotify.me()
                user = User.spotify_login(sp_user["email"])
                if not user:
                    User.signup(sp_user["display_name"], sp_user["email"], None, None)
                return redirect(url_for('home_page'))
            except Exception as e:
                print(e)

        # handle error for spotify login
        if request.args.get("error"):
            spotify_error = request.args.get("error")

        if not User.is_spotify_login():
            spotify_login_url = am.get_authorize_url()

        # load login page
        return render_template('login.html', spotify_login_url=spotify_login_url, spotify_error=spotify_error)


@app.route('/test-server-file-save')
def test_file_save():
    filename = '041a0a8b-7f4a-42f4-93ca-fb72d160611a'
    if request.args.get('file'):
        filename = request.args.get('file')

    my_file1 = os.path.join('/tmp', filename)
    my_file2 = os.path.join('/tmp/spotify_cache', filename)

    try:
        print('write with w+')
        print('write to /tmp')
        f = open(my_file1, "w+")
        f.write(json.dumps(request.args.get('code')))
        f.close()
        print('write to /tmp/spotify_cache')
        f = open(my_file2, "w+")
        f.write(json.dumps(request.args.get('code')))
        f.close()
    except IOError as e:
        print(e)
    except Exception as e:
        print(e)

    try:
        print('write with w')
        print('write to /tmp')
        f = open(my_file1, "w")
        f.write(json.dumps(request.args.get('code')))
        f.close()
        print('write to /tmp/spotify_cache')
        f = open(my_file2, "w")
        f.write(json.dumps(request.args.get('code')))
        f.close()
    except IOError as e:
        print(e)
    except Exception as e:
        print(e)

    return render_template('index.html', user=None)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    User.logout()
    session.clear()
    return redirect(url_for('home_page'))


def receiveRhythm():
    data = request.json
    return jsonify(data)


def adjustArray(array):
    newArray = []
    # if invalid array, don't consider it but still return it into the userResult
    if len(array) <= 3:
        newArray = [0]
        return newArray
    # dif = array[0]
    # for data in array:
    #     num = round((data - dif), 3)
    #     newArray.append(num)
    array.pop(0)
    return array


def arrayIntervals(array):
    # retrive the array intervals of timestamps
    newArray = []
    index = 1
    if len(array) <= 3:
        newArray = [0]
        return newArray

    for timestamp in array:
        if (index < len(array)):
            prev = array[index - 1]
            num = round((array[index] - prev), 3)
            newArray.append(num)
            index += 1
    newArray.pop(0)  # pop the first item in case user error
    return newArray


@app.route('/rhythm', methods=['GET', 'POST'])
def rhythmPost():
    if request.method == 'POST':
        out = receiveRhythm()
        # return time interval with first element dropped
        session['user_result'] = json.loads(request.data)
        #print(session['user_result'])
        return out

@app.route('/multiplier', methods=['GET', 'POST'])
def multiplierPost():
    if request.method == 'POST':
        multiplier = request.json
        # print(multiplier)

        global multiply
        multiply = json.loads(request.data)
        # print(multiply)

        return jsonify(multiplier)


@app.route('/melody', methods=['GET', 'POST'])
def melody():
    if request.method == 'POST':
        fileName = ''
        try:
            print("Received Audio File")
            if request.files.get('file'):
                outFile = request.files["file"]
                print(type(outFile))
                if request.headers['Host'] == "127.0.0.1:5000":
                    print("HELLO LOCAL SERVER")
                    fileName = outFile.filename
                else:
                    print("HELLO LIVE SERVER")
                    fileName = "/tmp/" + outFile.filename

                print("FILENAME = ", fileName)
                session['recording'] = fileName
                outFile.save(fileName)
                category = 'success'
                msg = 'melody recording saved, now going to results...'
            else:
                category = 'danger'
                msg = 'no file given'

        except Exception as e:
            print(e)
            category = 'danger'
            msg = e

        resp = {'feedback': msg, 'category': category, 'filename': fileName}
        return make_response(jsonify(resp), 200)


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'POST':
        # handle request
        rval = User.send_reset_password_email(request.form['email'])
        if rval:
            msg = "An email was sent with instructions to reset your password."
            category = "success"

        else:
            msg = str("Email not sent")
            category = "danger"

        resp = {'feedback': msg, 'category': category}
        return make_response(jsonify(resp), 200)
    else:
        return render_template('forgotPass.html')


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_pass():
    if request.method == 'POST':
        redirect_url = '/login'

        # check if valid reset token
        # its already checked in page load but can be issue if multiple forms were opened
        if User.is_valid_reset_token(request.form['token']):
            # check if password and confirmation match
            if request.form['password'] == request.form['confirm_password']:
                # continue with reset
                reset = User.reset_password(request.form['password'], request.form['token'])

                # check reset status
                if reset:
                    msg = "Password Reset!"
                    category = "success"
                else:
                    msg = "Password reset failed"
                    category = "danger"
            else:
                msg = "Password and confirmation do not match"
                category = "danger"
        else:
            msg = "Password reset failed. Invalid link."
            category = "danger"

        resp = {'feedback': msg, 'category': category, 'redirect_url': redirect_url}
        return make_response(jsonify(resp), 200)
    else:
        token = request.args.get('token')
        print(token)
        is_valid_token = False
        if token:
            is_valid_token = User.is_valid_reset_token(token)

        return render_template('resetPass.html', is_valid_token=is_valid_token, token=token)


@app.route('/source', methods=['GET', 'POST'])
def source():
    if request.method == 'POST':
        data = json.loads(request.data)
        title = data[0]
        artist = data[1]
        url = data[2]
        obj = Source(artist=artist, url=url, title=title)
        success = obj.process_input()

        if (success):
            """ADD SONG TO QUEUE"""
            # song = {
            #     "title": title,
            #     "artist": artist,
            #     "filepath": success
            # }
            # song = {'artist': [artist], 'title': [title], 'filepath': [success]}
            # """ADD TO CSV"""
            # df = pd.DataFrame.from_dict(data=song)
            # print(df)
            # df.to_csv('user_uploads.csv', mode='a', header=False, index=False, sep=',')
            # output = pd.read_csv('user_uploads.csv', header=0)
            # print(output.to_string)

            """SAVED IN ORDER ARTIST, TITLE, FILENAME"""
            row = [artist, title, success]
            with open(os.path.dirname(os.path.realpath(__file__)) + '/user_uploads.csv', 'a+', newline='') as write_obj:
                csv_writer = csv.writer(write_obj)
                csv_writer.writerow(row)

            """EXAMPLE ON READING AND PARSING"""
            # with open('user_uploads.csv') as csv_file:
            #     csv_reader = csv.reader(csv_file, delimiter=',')
            #     for row in csv_reader:
            #         print(row)

            resp = {"category": "success", "feedback": "Song analyzed and added to DB"}
            return make_response(jsonify(resp), 200)
        else:
            resp = {"category": "danger", "feedback": "Failed to analyze song"}
            return make_response(jsonify(resp), 200)


@app.route('/fileSource', methods=['GET', 'POST'])
def source2():
    """
    - downloads the file into the directed path
    - need to fetch ARTIST and TITLE fields
    """
    if request.method == 'POST':
        data = request.files["file"]

        # parses the filename to obtain artist, title, and file extension
        track_meta = data.filename[1:len(data.filename) - 1]
        track_meta = track_meta.replace("%22", "")
        meta_split = track_meta.split(',')
        meta_split[0] = meta_split[0][7:len(meta_split[0])]
        meta_split[1] = meta_split[1][6:len(meta_split[1])]
        meta_split[2] = meta_split[2][4:len(meta_split[2])]
        artist = meta_split[0]
        title = meta_split[1]
        print(meta_split)
        filename_ext = meta_split[len(meta_split) - 1]
        print(data.filename)
        print(data)

        # put together a unique filename to save
        filename_f = str(time.time() * 1000).replace('.', '') + "." + filename_ext

        if request.headers['Host'] == "127.0.0.1:5000":
            print("HELLO LOCAL SERVER")
            filename_path = filename_f
        else:
            print("HELLO LIVE SERVER")
            filename_path = "/tmp/" + filename_f

        data.save(filename_path)

        print("==================")
        print(data.filename)
        print(filename_ext)
        print(filename_path)
        print(type(data))
        #
        # print(artist)
        # print(type(artist))
        # print(title)
        # print(type(title))

        # process the user inputs to get the necessary info
        obj = Source(artist=artist, file=filename_path, title=title)
        success = obj.process_input()

        """SAVED IN ORDER ARTIST, TITLE, FILENAME"""
        row = [artist, title, success]
        with open(os.path.dirname(os.path.realpath(__file__)) + '/user_uploads.csv', 'a+', newline='') as write_obj:
            csv_writer = csv.writer(write_obj)
            csv_writer.writerow(row)

        if (success):
            resp = {"category": "success"}
            return make_response(jsonify(resp), 200)
        else:
            resp = {"category": "failure"}
            return make_response(jsonify(resp), 200)

        resp = {"category": "success"}
        return make_response(jsonify(resp), 200)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = json.loads(request.data)
        title = data[0]
        artist = data[1]
        songs = Song.get_by_title_artist(title=title, artist=artist)

        if(songs != None):
            data = []
            for song in songs:
                songItem = []
                songItem.append(song.title)
                songItem.append(song.artist)
                songItem.append(song.release_date)

                data.append(songItem)
            print(data)
            resp = {"category": "success", "data" : data}
            return make_response(jsonify(resp), 200)
        else:
            resp = {"category": "failure"}
            return make_response(jsonify(resp), 200)


@app.context_processor
def get_current_user():
    return {"uuid": str(uuid.uuid4()), "user": User.current_user()}


if __name__ == '__main__':
    app.run(debug=True)
