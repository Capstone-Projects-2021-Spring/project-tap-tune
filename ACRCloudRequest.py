import os, sys
from acrcloud.recognizer import ACRCloudRecognizer
import re

#TODO: Work on more metadata extraction, folder scan and output

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

    def set_title(self, title):
        self.title = title

    def set_artist(self, artists):
        self.artists = artists

    def set_genre(self, genres):
        self.genres = genres


class acrCloudRequest:
    def __init__(self):
        config = {
            # Should replace this with a more secure way of accessing identifiers maybe
            'host': 'identify-eu-west-1.acrcloud.com',
            'access_key': '5b08c65b811b20cfdfa300bca6c8a093',
            'access_secret': '8CLfpgyw75EcTqe9UWhhs821hemenq0NiiB4bVhn',
            'timeout': 10  # seconds
        }
        self.acr = ACRCloudRecognizer(config)

    def getACRSongFingerprint(self, userfile):
        # @param userfile: audio file path

        # Get fingerprinted song string from ACR Cloud
        fingerprinted = self.acr.recognize_by_file(userfile, 0)
        print(fingerprinted)

        # Gets rid of all special characters that may not be needed. Keeps commas and hyphens
        fingerprinted = re.sub('[^A-Za-z0-9,-_]+', '', fingerprinted)
        fingerprinted = re.sub(r'[\[\]\\\/]', '', fingerprinted)

        # Object for song metadata return
        songmetadata = foundsong()
        songStrings = ["title", "artists", "genres"]

        # Goes through to search for each metadata identifier from songStrings
        for identifiers in range(0, len(songStrings)):
            try:
                # String manipulation for each metadata field
                substr = fingerprinted[fingerprinted.index(songStrings[identifiers]) + len(songStrings[identifiers]) + 1:]
                print(substr)

                # Searches for multiple entries in each field like multiple genres or artists
                # multiple fields in identifier are separated by string "name:".
                # Will check until next ":" is not after "name", thus ending multiple fields for said identifier
                flag = 0
                counter = 8
                while flag == 0:
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
                substr = substr.split("name:")

                # Cleans up elements in each split string and puts into a single string
                substr = arrayToString(substr)

            # If metadata identifier is not found, sets string to empty and prints error
            except ValueError:
                print("No " + songStrings[identifiers] + " found")
                substr = ""

            # Bunch of if statements to make sure correct identifier is set to each attribute in the song object
            if songStrings[identifiers] == "title":
                songmetadata.set_title(substr)
            if songStrings[identifiers] == "artists":
                songmetadata.set_artist(substr)
            if songStrings[identifiers] == "genres":
                songmetadata.set_genre(substr)

        return songmetadata

    def getACRFingerPrint_Folder(self, folder):
        # Get all the files in the folder
        # This assumes all the files in the folder are .wav
        file_list = os.listdir(folder)

        # Makes sure nothing but songs are in the test
        file_songlist = []
        for files in range(len(file_list)):
            if ".wav" in file_list[files]:
                file_songlist.append(file_list[files])












#   TESTING   ###################################################################################################################

'''
folderDir = ""
file = ""
#file = "kaguya.wav"
obj = acrCloudRequest()
obj.getACRFingerPrint_Folder(folderDir)

song = obj.getACRSongFingerprint(file)
print(" ")
print(song.title)
print(song.artists)
print(song.genres)
'''


'''
folder = ""
print(os.listdir(folder))
'''