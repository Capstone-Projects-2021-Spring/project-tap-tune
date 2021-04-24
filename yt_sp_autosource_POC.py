from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import numpy as np
from youtubesearchpython import search
from models.Source import Source

def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])

"""
FUNCTION TO SEARCH SPOTIFY FOR THE SONG DURATION
@param title - title of the song to be searched
@param artist - artist of the song to be searched, used for verification
return retObj
failure - resObj['duration'] = None
success - resObj['duration'] = <int>
"""
def sp_search_convert(title, artist):
    retObj = {
        'duration': None
    }
    spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="596f71278da94e8897cb131fb074e90c",
                                                                    client_secret="a13cdd7f3a8c4f50a7fc2a8dba772386"))

    sp_res = spotify.search(q=title, limit=20, type='track')

    for track in sp_res['tracks']['items']:
        for sp_artist in track['artists']:
            sim = levenshtein_ratio_and_distance(artist, sp_artist['name'], ratio_calc=True)
            print(sim)

            if (sim > .5):
                sp_duration = track['duration_ms']
                sp_duration = sp_duration // 1000
                retObj['duration'] = sp_duration
                return retObj

    return None

"""
FUNCTION TO SEARCH FOR YOUTUBE VIDEO, GET DURATION AND URL
@param title - title of the song to be searched
@param artist - artist of the song to be searched, used for verification
return retObj
"""
def yt_search_convert(title, artist):
    retObj = {
        'duration': None,
        'url': None
    }
    yt_res = search.VideosSearch(query=(artist+" "+title+" Audio"), limit = 1).result()

    if(yt_res):
        yt_duration = yt_res['result'][0]['duration']
        yt_duration = yt_duration.split(':')
        retObj['duration'] = int(yt_duration[0])*60 + int(yt_duration[1])
        retObj['url'] = yt_res['result'][0]['link']

        return retObj

    else:
        return None

class AutoSource:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

    def process_info(self):
        sp_val = sp_search_convert(self.title, self.artist)
        yt_val = yt_search_convert(self.title, self.artist)

        print(sp_val)
        print("++++++++++++++++++++++++++++++++++")
        print(yt_val)
        if(sp_val and yt_val):
            if( abs(sp_val['duration'] - yt_val['duration']) < 15):
                obj = Source(artist=self.artist, url=yt_val['url'], title=self.title)
                success = obj.process_input()

                if(success):
                    return 1

                else:
                    return 0

            else:
                return 0

        else:
            return 0

if __name__ == "__main__":
    AutoSource.process_info("another one bitess the dust", "queen")