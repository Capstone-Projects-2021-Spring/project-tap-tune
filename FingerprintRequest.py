import os, sys
from acrcloud.recognizer import ACRCloudRecognizer
import re
import acrcloud.acrcloud_extr_tool as ACRext
import requests
import json

#TODO: Work on more metadata extraction

# Function to turn array of individual strings from split function into one string
def arrayToString(array):

    string = ""

    # eliminate special characters from each string and add to temp string. Skip if element is empty
    for elements in array:
        text = re.sub('[^A-Za-z0-9-_]+', '', elements)
        if elements == "":
            continue
        else:
            string += text + ","

    # if the string ends with a comma, remove from final string
    if string[len(string) - 1] == ',':
        string = string[:len(string) - 1]

    return string



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

        # Get fingerprinted song string from ACR Cloud
        fingerprinted = self.acr.recognize_by_file(userfile, 0)
        #print(fingerprinted)

        #Service Specific naming convention
        songStrings = ["title", "artists", "genres","score"]

        song = parseJSON(fingerprinted, songStrings)
        return song

    def getAudDFingerprint(self, userpath):

        files = {
            'file': open(userpath, 'rb'),
        }

        # Apparently this one is use for humming and such, but has low accuracy.
        result = requests.post('https://api.audd.io/recognizeWithOffset/  ', data=self.data, files=files)
        # print(result.text)
        # result = requests.post('https://api.audd.io/ ', data=self.data, files=files)

        # Service Specific naming convention
        songStrings = ["title", "artists", "genreNames", "score"]

        song = parseJSON(result.text, songStrings)
        return song

    def searchFingerprintAll(self, userfile):
        audDfoundSong = self.getAudDFingerprint(userfile)
        ACRfoundSong = self.getACRSongFingerprint(userfile)

        mergedSong = foundsong()

        if (audDfoundSong.title == ""):
            return ACRfoundSong
        elif (ACRfoundSong.title == ""):
            return audDfoundSong


        text = re.sub('[^A-Za-z0-9-_]+', '', audDfoundSong.title)
        text2 = re.sub('[^A-Za-z0-9-_]+', '', ACRfoundSong.title)

        if (text > text2 or text == text2):
            mergedSong.title = audDfoundSong.title
        else:
            mergedSong.title = ACRfoundSong.title

        text = re.sub('[^A-Za-z0-9-_]+', '', audDfoundSong.artists)
        text2 = re.sub('[^A-Za-z0-9-_]+', '', ACRfoundSong.artists)

        if (text > text2 or text == text2):
            mergedSong.title = audDfoundSong.artists
        else:
            mergedSong.title = ACRfoundSong.artists

        text = re.sub('[^A-Za-z0-9-_]+', '', audDfoundSong.genres)
        text2 = re.sub('[^A-Za-z0-9-_]+', '', ACRfoundSong.genres)

        if (text > text2 or text == text2):
            mergedSong.title = audDfoundSong.genres
        else:
            mergedSong.title = ACRfoundSong.genres

        return mergedSong




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



def parseJSON(fingerprinted, songStrings):
    # Gets rid of all special characters that may not be needed. Keeps commas and hyphens
    print(fingerprinted)
    fingerprinted = re.sub('[^A-Za-z0-9,-_]+', '', fingerprinted)
    fingerprinted = re.sub(r'[\[\]\\\/]', '', fingerprinted)

    # Object for song metadata return
    songmetadata = foundsong()

    # Goes through to search for each metadata identifier from songStrings
    for identifiers in range(0, len(songStrings)):
        try:
            # String manipulation for each metadata field
            substr = fingerprinted[fingerprinted.index(songStrings[identifiers]) + len(songStrings[identifiers]) + 1:]
            # print(substr)

            # Searches for multiple entries in each field like multiple genres or artists
            # multiple fields in identifier are separated by string "name:".
            # Will check until next ":" is not after "name", thus ending multiple fields for said identifier
            flag = 0
            counter = 8
            while flag == 0:
                #print(substr[counter - 8:counter])
                if len(substr) == counter:
                    flag = 1
                else:
                    if substr[counter] == ':':
                        if "name" in substr[counter - 8:counter]:
                            counter += 1
                        else:
                            flag = 1
                counter += 1

            # More String clean up. Counter will have an index that will encompass all the fields of identifier
            # Splits string to get names of each field
            substr = substr[:counter]
            substr = substr[:substr.rindex(",")]
            if "name" in substr:
                substr = substr.split("name:")
            else:
                substr = substr.split(",")

            # Cleans up elements in each split string and puts into a single string
            substr = arrayToString(substr)

        # If metadata identifier is not found, sets string to empty and prints error
        except ValueError:
            #print("No " + songStrings[identifiers] + " found")
            substr = ""

        # Bunch of if statements to make sure correct identifier is set to each attribute in the song object
        if "title" in songStrings[identifiers]:
            songmetadata.set_title(substr)
        if "artist" in songStrings[identifiers]:
            songmetadata.set_artist(substr)
        if "genre" in songStrings[identifiers]:
            songmetadata.set_genre(substr)
        if "score" in songStrings[identifiers]:
            songmetadata.set_score(substr)

    return songmetadata










#   TESTING   ##################################################################################################################

obj = FingerprintRequest()

file = r"C:\Users\\2015d\OneDrive\Desktop\.wav files\scuffed.mp3"

acrSong = obj.getACRSongFingerprint(file)
print(acrSong.title)
print(acrSong.artists)
print(acrSong.genres)
print(acrSong.score)

audDSong = obj.getAudDFingerprint(file)
print(audDSong.title)
print(audDSong.artists)
print(audDSong.genres)
print(audDSong.score)

lastTest = obj.searchFingerprintAll(file)
print(lastTest.title)
print(lastTest.artists)
print(lastTest.genres)
print(lastTest.score)

'''
folderDir = ""
foldersonglist = obj.getACRFingerPrint_Folder(folderDir)
'''
