import os, sys
from acrcloud.recognizer import ACRCloudRecognizer
import re


def arrayToString(array):
    string = ""
    for elements in array:
        text = re.sub('[^A-Za-z0-9-_]+', '', elements)
        if elements == "":
            continue
        else:
            string += text + ","

    if string[len(string) - 1] == ',':
        string = string[:len(string) - 1]

    return string


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

        }
        self.acr = ACRCloudRecognizer(config)

    def getACRSongFingerprint(self, userfile):
        # Get fingerprinted song string from ACR Cloud
        fingerprinted = self.acr.recognize_by_file(userfile, 0)

        # Clean up the string for data extract
        fingerprinted = re.sub('[^A-Za-z0-9,-_]+', '', fingerprinted)
        fingerprinted = re.sub(r'[\[\]\\\/]', '', fingerprinted)

        songmetadata = foundsong()
        songStrings = ["title", "artists", "genres"]

        # Goes through to search for each metadata
        for identifiers in range(0, len(songStrings)):
            try:
                # String manipulation for each metadata field
                substr = fingerprinted[fingerprinted.index(songStrings[identifiers]) + len(songStrings[identifiers]) + 1:]
                #print(substr)

                # Searches for multiple entries in each field like multiple genres or artists
                flag = 0
                counter = 8
                while flag == 0:
                    if substr[counter] == ':':
                        if "name" in substr[counter - 8:counter]:
                            counter += 1
                        else:
                            flag = 1
                    counter += 1

                # More String clean up
                substr = substr[:counter]
                substr = substr[:substr.rindex(",")]
                substr = substr.split("name:")

                # Cleans up elements in each split string and puts into a single string
                substr = arrayToString(substr)
            except ValueError:
                print("No " + songStrings[identifiers] + " found")
                substr = ""

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
arr = ['', 'MasayukiSuzuki,', 'AiriSuzuki']
print(arrayToString(arr))

folderDir = "C:\\Users\\2015d\OneDrive\Desktop\.wav files"
# file = ""C:\\Users\\2015d\OneDrive\Desktop\.wav files\DaftPuck_OneMoreTime.wav""
file = "kaguya.wav"
obj = acrCloudRequest()
obj.getACRFingerPrint_Folder(folderDir)

song = obj.getACRSongFingerprint(file)
print(" ")
print(song.title)
print(song.artists)
print(song.genres)
'''


'''
folder = "C:\\Users\\2015d\OneDrive\Desktop\.wav files"
print(os.listdir(folder))
'''