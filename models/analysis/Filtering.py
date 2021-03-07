# Filtering class
# Accepts RhythmRecording Array
# Makes SQL Queries to the Database (ours or ACR Cloud) For Artist and Genre, Calls Web Scraper for Lyrics
# Class with fields result_artist result_lyrics, result_genre representing potential songs (Song Class or Strings)
# Do I need a recording ID?

import lyricsgenius
from models.Database import db, get_cursor

class Filtering:
    """
    constructor Filtering class constructor
    Artist : String
    Genre : String
    Lyrics : String
    parameters set to none if not provided by user
    """
    def __init__(self, Artist = None, Genre = None, Lyrics = None):
        self.input_artist = Artist
        self.input_genre = Genre
        self.input_lyrics = Lyrics

    """
    Filter through database for records by input_artist
    Populates populates result_artist with filtered song titles
    Return : Data retrieved from db from filtering (success)
    Return : None (failure)
    """
    def filterArtist(self):

        #checks that field is valid
        if(self.input_artist):
            try:
                #retrieves cursor from Database.py
                cursor = get_cursor()
                cursor.execute('SELECT * FROM song WHERE artist = %s', (self.input_artist, ))
                #fetch al results and save in song_data list
                song_data = cursor.fetchall()
                return song_data
                
            except Exception as e:
                 print(e)
                 return None
        
        else:

            return None
    
    """
    Filter through database for records by input_genre
    Populates populates result_genre with filtered song titles
    Return : 1 (success)
    Return : 0 (failure)
    """
    def filterGenre(self):

        #checks that field is valid
        if(self.input_genre):

            return 1

        else:

            return 0

    """
    use lyricsgenius package to webscrape the Genius song collection based on input_lyrics
    Populates populates result_lyric with found song titles
    Return : List of artist/title pairs found from the lyric filtering (success)
    Return : None (failure)
    """
    def filterLyrics(self):

        #checks that field is valid
        if(self.input_lyrics):

            #START of POC
            client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"

            genius = lyricsgenius.Genius(client_access_token)
            song_data = []
            #for loop to increase number of results (current:500)
            for x in range (1,10):

                #makes request to genius API and wrapper to search through lyrics 
                request = genius.search_lyrics(self.input_lyrics, per_page=50, page=(1*x))
                #goes through 50 songs and inserts data in song_data list
                for hit in request['sections'][0]['hits']:
                    artist_name = hit['result']['primary_artist']['name']
                    song_title = hit['result']['title']

                    song_data.append( (artist_name + "-" + song_title) )
            return song_data

        else:

            return None
    
    """
    Execution function, ordered so that most specific field is followed by least specific
    """
    def filterRecording(self):
        filterArtist(self)
        filterGenre(self)
        filterLyrics(self)

# do any testing in here
if __name__ == ("__main__"):
    obj = Filtering(Lyrics = "We Will Rock You")
    success = obj.filterLyrics()
    print("\n"+success)