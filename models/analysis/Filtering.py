# Filtering class
# Accepts RhythmRecording Array
# Makes SQL Queries to the Database (ours or ACR Cloud) For Artist and Genre, Calls Web Scraper for Lyrics
# Class with fields result_artist result_lyrics, result_genre representing potential songs (Song Class or Strings)
# Do I need a recording ID?

import lyricsgenius


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
    Return : 1 (success)
    Return : 0 (failure)
    """
    def filterArtist(self):

        #checks that field is valid
        if(self.input_artist):

            return 1
        
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
    Return : 1 (success)
    Return : 0 (failure)
    """
    def filterLyrics(self):

        #checks that field is valid
        if(self.input_lyrics):

            #START of POC
            client_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"

            genius = lyricsgenius.Genius(client_access_token)

            for x in range (1,10):
                request = genius.search_lyrics(self.input_lyrics, per_page=50, page=(1*x))
                for hit in request['sections'][0]['hits']:
                    artist_name = hit['result']['primary_artist']['name']
                    song_title = hit['result']['title']

                    print(artist_name + " - " + song_title)
            
            #END of cPOC

            return 1

        else:

            return 0
    
    """
    Execution function, ordered so that most specific field is followed by least specific
    """
    def filterRecording(self):
        filterArtist(self)
        filterGenre(self)
        filterLyrics(self)

if __name__ == ("__main__"):
    obj = Filtering(Lyrics = "We Will Rock You")
    success = obj.filterLyrics()
    print("\n"+success)