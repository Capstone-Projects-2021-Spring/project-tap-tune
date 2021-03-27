
from acrcloud.recognizer import ACRCloudRecognizer
import re
import acrcloud.acrcloud_extr_tool as ACRext
import requests
import json
from models.Song import Song

#TODO: Work on more metadata extraction

def cleanString(string):
    # Gets rid of all special characters that may not be needed. Keeps commas and hyphens
    newString = re.sub('[^A-Za-z0-9,-_ ]+', '', string)
    newerString = re.sub(r'[\[\]]', '', newString)

    if "name: " in newString:
        returnString = newerString.replace("name: ", '')
    else:
        returnString = newerString

    return returnString

# Song object for returning the song found from ACRCloud
# Can Add attributes if extra metadata extraction is needed
class foundsong:
    def __init__(self):
        self.title = ""
        self.artists = ""
        self.genres = ""
        self.score = ""

        # Only for auto database input
        self.path = ""

    def set_title(self, title):
        self.title = title

    def set_artist(self, artists):
        self.artists = artists

    def set_genre(self, genres):
        self.genres = genres

    def set_score(self, score):
        self.score = score

    # Only for auto database input
    def set_path(self, path):
        self.path = path


class FingerprintRequest:
    def __init__(self):
        config = {
            # Should replace this with a more secure way of accessing identifiers maybe
            'host': 'identify-eu-west-1.acrcloud.com',
            'access_key': '5b08c65b811b20cfdfa300bca6c8a093',
            'access_secret': '8CLfpgyw75EcTqe9UWhhs821hemenq0NiiB4bVhn',
            'timeout': 10  # seconds
        }
        self.acr = ACRCloudRecognizer(config)

        self.data = {
            'return': 'apple_music,spotify',
            'api_token': '5e3d89525fdf63a5f5ef79f3ae87db68'
        }

    def getACRSongFingerprint(self, userfile):
        # @param userfile: audio file path

        songArray = list()
        returnsong = foundsong()

        # Get fingerprinted song string from ACR Cloud
        fingerprinted = self.acr.recognize_by_file(userfile, 0)
        #print(fingerprinted)

        fingerprintJson = json.loads(fingerprinted)

        if 'Success' not in fingerprintJson['status']['msg']:
            print('ACRCloud: not found')
        else:

            songlist = (fingerprintJson['metadata']['music'][0])

            returnsong.title = cleanString(str(songlist['title']))
            returnsong.artist = cleanString(str(songlist['artists']))
            returnsong.genre = cleanString(str(songlist['genres']))
            # returnsong.set_score(cleanString(str(songlist['score'])))
        return returnsong

    def getAudDFingerprint(self, userpath):
        files = {
            'file': open(userpath, 'rb'),
        }
        returnsong = foundsong()

        # Apparently this one is use for humming and such, but has low accuracy.
        # result = requests.post('https://api.audd.io/recognizeWithOffset/  ', data=self.data, files=files)
        result = requests.post('https://api.audd.io/ ', data=self.data, files=files)

        #print(result.text)

        fingerprintJson = json.loads(result.text)

        if 'success' not in fingerprintJson['status']:
            print('AudD: not found')
        else:
            songlist = (fingerprintJson['result'])

            returnsong.set_title(cleanString(str(songlist['title'])))
            returnsong.set_artist(cleanString(str(songlist['apple_music']['artistName'])))
            returnsong.set_genre(cleanString(str(songlist['apple_music']['genreNames'])))
            # returnsong.set_score(cleanString(str(songlist['score'])))

        return returnsong


    def getHummingFingerprint(self, userpath):

        files = {
            'file': open(userpath, 'rb'),
        }

        songArray = list()

        # Apparently this one is use for humming and such, but has low accuracy.
        result = requests.post('https://api.audd.io/recognizeWithOffset/  ', data=self.data, files=files)
        # result = requests.post('https://api.audd.io/ ', data=self.data, files=files)

        fingerprintJson = json.loads(result.text)

        if 'success' not in fingerprintJson['status']:
            print('AudD Humming: not found')
        else:
            songlist = (fingerprintJson['result']['list'])
            for songs in range(len(songlist)):
                returnsong = foundsong()
                returnsong.set_title(cleanString(str(songlist[songs]['title'])))
                returnsong.set_artist(cleanString(str(songlist[songs]['artist'])))
                # returnsong.set_genre(cleanString(songlist[songs]['genre']))))
                returnsong.set_score(cleanString(str(songlist[songs]['score'])))

                songArray.append(returnsong)

        return songArray


    def searchFingerprintAll(self, userfile):

        #Weighted AudD first, then ACR, then humming
        audDfoundSong = self.getAudDFingerprint(userfile)
        ACRfoundSong = self.getACRSongFingerprint(userfile)
        hummingFingerprint = self.getHummingFingerprint(userfile)

        result = foundsong()

        if audDfoundSong.title:
            result.title = audDfoundSong.title
            result.artist = audDfoundSong.artists
            result.genre = audDfoundSong.genres
            # result.set_score(audDfoundSong.score)
        else:
            if ACRfoundSong.title:
                result.title = ACRfoundSong.title
                result.artist = ACRfoundSong.artists
                result.genre = ACRfoundSong.genres
                # result.set_score(ACRfoundSong.score)
            else:
                result.title = hummingFingerprint[0].title
                result.artist = hummingFingerprint[0].artists
                result.genre = hummingFingerprint[0].genres
                # result.set_score(hummingFingerprint[0].score)

        return result



'''
    # This will NOT be used for final implementation. This will primarily be used for backend automatic database insert
    # Returns a list of song objects with respective metadata and path to actual song file
    def getACRFingerPrint_Folder(self, folder):

        # Get all the files in the folder
        # This assumes all the files in the folder are .wav
        file_list = os.listdir(folder)
        print(file_list)

        # Makes a list of the absolute path to that file for ACRCloud file access
        file_abs_path = []
        for x in range(len(file_list)):
            file_abs_path.append(folder + "\\" + file_list[x])

        # Makes sure nothing but songs are in the test by checking the end of the path name
        file_songList = []
        for x in range(len(file_abs_path)):
            if ".wav" in file_abs_path[x][len(file_abs_path[x]) - 6:]:
                file_songList.append(file_abs_path[x])

        # Uses the in class getACRSongFingerprint to get the metadata for each of the songs
        # Saves the path to the file as attribute in Song Object for hashing later
        file_returnList = []
        for x in range(len(file_songList)):
            print("" + str(x + 1) + ": Finding Metadata for " + file_songList[x])
            song = self.getACRSongFingerprint(file_songList[x])
            song.set_path(file_songList[x])
            file_returnList.append(song)

        print("Task Complete!")
        return file_returnList
'''










#   TESTING   ##################################################################################################################

obj = FingerprintRequest()

file = r"C:\\Users\\2015d\OneDrive\Desktop\.wav files\scuffed.mp3"

'''
acrSong = obj.getACRSongFingerprint(file)
print(acrSong.title)
print(acrSong.artists)
print(acrSong.genres)
print(acrSong.score)
'''
'''
audDSong = obj.getAudDFingerprint(file)
print(audDSong.title)
print(audDSong.artists)
print(audDSong.genres)
print(audDSong.score)
'''

'''
lastTest = obj.searchFingerprintAll(file)
print(lastTest.title)
print(lastTest.artists)
print(lastTest.genres)
print(lastTest.score)
'''
