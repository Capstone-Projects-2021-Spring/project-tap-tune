# Filtering class
# Accepts RhythmRecording Array
# Makes SQL Queries to the Database (ours or ACR Cloud) For Artist and Genre, Calls Web Scraper for Lyrics
# Class with fields result_artist result_lyrics, result_genre representing potential songs (Song Class or Strings)
# Do I need a recording ID?

import lyricsgenius
# from models.testDatabase import db, get_cursor
from models.Database import db, get_cursor


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

                result_data.append({"title": title, "artist": artist, "genres": genres})

            # if there was a valid list of songs passed through
            if (song_results != None):
                # go through song_results and look for a song match
                for artist_track in result_data:
                    for genre_track in song_results:
                        if (genre_track["title"] == artist_track["title"]):
                            return_data.append(artist_track)
                            match = match + 1
                if match > 0:
                    return return_data
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

    def filterGenre(self, song_results):
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

                """APPEND NEW SET OF TRACKS TO THE LIST"""
                result_data.append({"title": title, "artist": artist, "genres": genres})

            """
            ***INSERT THE COMPARISON TO RHYTHM ANALYSIS RESULTS HERE
            """

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

        """LYRICGENIUS SSTUP"""
        client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"
        genius = lyricsgenius.Genius(client_access_token)
        result_data = []

        # makes request to genius API and wrapper to search through lyrics
        request = genius.search_lyrics(self.input_lyrics, per_page=50, page=(1))

        """PARSE DATA FOR ARTIST NAME AND SONG TITLE"""
        for hit in request['sections'][0]['hits']:
            artist_name = hit['result']['primary_artist']['name']
            song_title = hit['result']['title']
            result_data.append({"title": song_title, "artist": artist_name})

        """CHECKS TO SEE IF VALID LIST OF SONGS WAS PASSED"""
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
            # CHECK IF THERE WERE ANY MATCHES
            if match > 0:
                return return_data
            else:
                return song_results

        # if no valid song_results is passed
        else:
            return result_data

        return song_data


    def dupCheck(self, dict, target):
        for track in dict:
            if target in track:
                pass
            else:
                return False
        return True
    """
    Execution function, ordered so that most specific field is followed by least specific
    """
    def filterRecording(self, a_list=None):
        print(a_list)
        r_list = a_list

        """
        CHECKS FOR ANY GENRE INPUT
        """
        if(self.input_genre):
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
            print("LIST FILTERED BY ARTIST")
            print(r_list)

        else:
             print("NO GENRE INPUT")

        """
        CHECKS FOR ANY LYRICS INPUT
        """
        if(self.input_lyrics):
            r_list = self.filterLyrics(r_list)
            print("LIST FILTERED BY LYRICS")
            print(r_list)

        else:
            print("NO LYRICS INPUT")

        # returns the list filtered by provided fields
        return r_list