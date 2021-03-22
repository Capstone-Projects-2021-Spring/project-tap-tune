# Filtering class
# Accepts RhythmRecording Array
# Makes SQL Queries to the Database (ours or ACR Cloud) For Artist and Genre, Calls Web Scraper for Lyrics
# Class with fields result_artist result_lyrics, result_genre representing potential songs (Song Class or Strings)
# Do I need a recording ID?

import lyricsgenius
import spotipy
import json
from models.Database import db, get_cursor

# Set user's credencials to access Spotify data
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'


creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
spotify = spotipy.Spotify(client_credentials_manager=creds)

class Filtering:
    """
    constructor Filtering class constructor
    Artist : String
    Genre : String
    Lyrics : String
    parameters set to none if not provided by user
    """

    def __init__(self, Artist=None, Genre=None, Lyrics=None):
        self.input_artist = Artist
        self.input_genre = Genre
        self.input_lyrics = Lyrics

    """
    Filter through database for records by input_artist
    Populates populates result_artist with filtered song titles
    Return : Data retrieved from db from filtering (success)
    Return : None (failure)
    """

    def filterArtist(self, song_results):
        # checks that field is valid
        match = 0
        try:
            # retrieves cursor from Database.py
            cursor = get_cursor()
            cursor.execute('SELECT * FROM song WHERE artist = %s', (self.input_artist,))
            # fetch al results and save in song_data list

            """GO THROUGH DB DATA"""
            song_data = cursor.fetchall()
            return_data = []
            result_data = []
            for track in song_data:
                title = track["title"]
                artist = track["artist"]
                genres = track["genre"]

                id =  track["id"]

                """SEARCH THROUGH SPOTIFY FOR AUDIO SAMPLE FILES"""
                results_1 = spotify.search(q=title, limit=10, type="track", market=None)
                preview = "None"
                for album in results_1["tracks"]["items"]:
                    albumArtist = album["artists"][0]
                    if(albumArtist["name"] == artist):
                        if (album["preview_url"]):  
                            preview = album["preview_url"]
                        break 

                result_data.append({"title": title, "artist": artist, "genres": genres, "id": id, "spotifyPreview": preview})

            """PERFORMS CROSS COMPARISON WITH PREVIOUS SONG LISTS"""
            # if there was a valid list of songs passed through
            if (song_results != None):
                # go through song_results and look for a song match
                for artist_track in result_data:
                    for track in song_results:
                        if (track["title"] == artist_track["title"]):
                            return_data.append(artist_track)
                            match = match + 1
                # if there are any matches return the cross compared list of songs
                if match > 0:
                    return return_data
                # if there are no matches return song_result
                else:
                    return song_results
            # if no valid song_results is passed
            else:
                return result_data

        except Exception as e:
            print(e)
            return None

    """
    Filter through database for records by input_genre
    Populates populates result_genre with filtered song titles
    Return : 1 (success)
    Return : 0 (failure)
    """

    def filterGenre(self, song_results = None):
        try:
            # retrieves cursor from Database.py
            cursor = get_cursor()
            cursor.execute(('SELECT * FROM song WHERE genre LIKE "%{0}%"').format(self.input_genre))
            # fetch al results and save in song_data list
            song_data = cursor.fetchall()

            """GO THROUGH SQL AND EXTRACT SPECIFIC DATA FIELDS"""
            result_data = []
            for track in song_data:
                title = track["title"]
                artist = track["artist"]
                genres = track["genre"]

                id = track["id"]

                """SEARCH SPOTIFY FOR A SAMPLE AUDIO FILE"""
                results_1 = spotify.search(q=title, limit=10, type="track", market=None)
                preview = "None"
                for album in results_1["tracks"]["items"]:
                    albumArtist = album["artists"][0]
                    if(albumArtist["name"] == artist):
                        if (album["preview_url"]):  
                            preview = album["preview_url"]
                        break 

                """APPEND NEW SET OF TRACKS TO THE LIST"""
                result_data.append({"title": title, "artist": artist, "genres": genres, "id": id, "spotifyPreview": preview})

            """COMPARE THE RESULT LIST WITH ANY PRIOR SONGS"""
            # result_final = []
            #
            # if(song_results != None):
            #     for track_1 in song_results:
            #         for track_2 in result_data:
            #             if(track_1["title"] == track_2["title"]):
            #                 if (self.dupCheck(result_final, track_2["title"])):
            #                     result_final.append(track_2)
            #     if (len(result_final) > 0):
            #         return result_data
            #
            #     else:
            #         return result_final
            #
            #
            # else:
            #     return result_data

            return result_data

        except Exception as e:
            print(e)
            return None

    """
    use lyricsgenius package to webscrape the Genius song collection based on input_lyrics
    Populates populates result_lyric with found song titles
    Return : List of artist/title pairs found from the lyric filtering (success)
    Return : None (failure)
    """
    def filterLyrics(self, song_results):
        match = 0

        """LYRICGENIUS SETUP"""
        client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"
        genius = lyricsgenius.Genius(client_access_token)
        result_data = []

        # makes request to genius API and wrapper to search through lyrics
        request = genius.search_lyrics(self.input_lyrics, per_page=50, page=(1))

        """PARSE DATA FOR ARTIST NAME AND SONG TITLE"""
        for hit in request['sections'][0]['hits']:
            artist_name = hit['result']['primary_artist']['name']
            song_title = hit['result']['title']

            """SEARCH SPOTIFY FOR AUDIO SAMPLE FILES"""
            results_1 = spotify.search(q=song_title, limit=10, type="track", market=None)
            preview = "None"
            for album in results_1["tracks"]["items"]:
                artist = album["artists"][0]
                if(artist["name"] == artist_name):
                    if (album["preview_url"]):  
                        preview = album["preview_url"]
                    break  

            result_data.append({"title": song_title, "artist": artist_name, "spotifyPreview": preview})

        """CROSS COMPARE LYRIC SEARCHES WITH SONG RESULTS"""
        # if there was a valid song list passed
        if (song_results != None):
            return_data = []

            # go through song_results and look for a song match
            for res_track in song_results:
                print("\n****************\n checking the list", res_track)
                for lyric_track in result_data:

                    # CHECK IF SONG TITLES MATHC, ADD THE TRACK TO THE RESULT AND INCREMENT MATCH
                    if (lyric_track["title"] == res_track["title"]):
                        if (self.dupCheck(return_data, lyric_track["title"])):
                            return_data.append(res_track)
                            match = match + 1
            # if there are matches found return the cross compared list
            if match > 0:
                return return_data
            else:
                return song_results

        # if no valid song_results is passed DON'T RETURN LIST BECASUE WE DON'T HAVE THEM
        else:
            return None


    def dupCheck(self, dict, target):
        for track in dict:
            if target in track:
                pass
            else:
                return False
        return True

    """
    Execution function, ordered so that most specific field is followed by least specific
    EDITS TO MAKE
    - DOES NOT ACCEPT A_LIST
    - FILTER FLOW IS GENRE->ARTIST->LYRICS --> SONG ANALYSIS
    - STORE THE SONG ID
    - RETURN A LIST OF SONGS [ {"TITLE", "ARTIST", "GENRES", "ID"] }
    """
    def filterRecording(self, a_list=None):
        r_list = []

        """
        CHECKS FOR ANY GENRE INPUT
        """
        if(self.input_genre) and (self.input_genre != "Metal"):
            r_list = self.filterGenre(r_list)
            print("*****LIST FILTERED BY GENRE")
            print(r_list)
        else:
            print("NO GENRE INPUT")

        """
        CHECKS FOR ANY ARTIST INPUT
        """
        if(self.input_artist):
            r_list = self.filterArtist(r_list)
            print("LIST FILTERED BY ARTIST " + self.input_artist)
            print(r_list)

        else:
             print("NO Artist INPUT")

        """
        CHECKS FOR ANY LYRICS INPUT
        """
        if(self.input_lyrics):
            r_list = self.filterLyrics(r_list)
            print("LIST FILTERED BY LYRICS " + self.input_lyrics)
            print(r_list)

        else:
            print("NO LYRICS INPUT")

        # returns the list filtered by provided fields
        print(r_list)
        return r_list