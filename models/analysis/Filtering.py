# Filtering class
# Accepts RhythmRecording Array
# Makes SQL Queries to the Database (ours or ACR Cloud) For Artist and Genre, Calls Web Scraper for Lyrics
# Class with fields result_artist result_lyrics, result_genre representing potential songs (Song Class or Strings)
# Do I need a recording ID?

import lyricsgenius
import spotipy
from models.Song import Song

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
        pop_check = False
        result_data = []

        # if there is a valid song resutls
        # loop through song_results and filter out artist names
        if( song_results != None):
            for track in song_results:
                if(track.artist == self.input_artist):
                    result_data.append(track)
                    pop_check = True

        # if no song results create new set of song results
        if(pop_check == False):
            """GO THROUGH DB DATA"""
            song_data = Song.get_by_artist(self.input_artist)
            for track in song_data:
                title = track.title
                artist = track.artist

                """SEARCH THROUGH SPOTIFY FOR AUDIO SAMPLE FILES"""
                results_1 = spotify.search(q=title, limit=10, type="track", market=None)
                preview = "None"
                for album in results_1["tracks"]["items"]:
                    albumArtist = album["artists"][0]
                    if(albumArtist["name"] == artist):
                        if (album["preview_url"]):
                            preview = album["preview_url"]
                        break
                track.set_preview(preview=preview)
                result_data.append(track)


        return result_data

    """
    Filter through database for records by input_genre
    Populates populates result_genre with filtered song titles
    Return : 1 (success)
    Return : 0 (failure)
    """

    def filterGenre(self):
        try:
            song_data = Song.get_by_genre(self.input_genre)
            """GO THROUGH SQL AND EXTRACT SPECIFIC DATA FIELDS"""
            result_data = []
            for track in song_data:
                title = track.title
                artist = track.artist

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
                track.set_preview(preview=preview)
                result_data.append(track)

            return result_data
        except Exception as e:
            print("FAILED TO SEARCH FOR GENRE")
            return []


    """
    Function to create a basically empty song for the lyric filter
    """
    def lyric_song(self, artist, title):
        song = Song(song_id=None, title=title, artist=artist, release_date=None, genre=None, onset_hash=None,
                    peak_hash=None, perc_hash=None, harm_hash=None)

        return song


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

        try:
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

                song = self.lyric_song(artist=artist_name, title=song_title)
                song.preview = preview
                result_data.append(song)
            """CROSS COMPARE LYRIC SEARCHES WITH SONG RESULTS"""
            # if there was a valid song list passed
            if (song_results != None):
                return_data = []

                # go through song_results and look for a song match
                for para_track in song_results:
                    for lyric_track in result_data:
                        # CHECK IF SONG TITLES MATHC, ADD THE TRACK TO THE RESULT AND INCREMENT MATCH
                        if (lyric_track.title == para_track.title):
                            return_data.append(para_track)
                            match += 1

                # if there are matches found return the cross compared list
                if match > 0:
                    return return_data
                else:
                    return song_results

            # if no valid song_results is passed DON'T RETURN LIST BECASUE WE DON'T HAVE THEM
            else:
                return result_data
        except Exception as e:
            print(e)
            return result_data


    """
    Execution function, ordered so that most specific field is followed by least specific
    EDITS TO MAKE
    - DOES NOT ACCEPT A_LIST
    - FILTER FLOW IS GENRE->ARTIST->LYRICS --> SONG ANALYSIS
    - STORE THE SONG ID
    - RETURN A LIST OF SONGS [ {"TITLE", "ARTIST", "GENRES", "ID"] }
    """
    def filterRecording(self):
        r_list = []

        """
        CHECKS FOR ANY GENRE INPUT
        """
        if(self.input_genre) and (self.input_genre != "None"):
            r_list = self.filterGenre()
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

if __name__ == "__main__":
    obj = Filtering(Artist="Prince")
    results = obj.filterRecording()
    print(results)