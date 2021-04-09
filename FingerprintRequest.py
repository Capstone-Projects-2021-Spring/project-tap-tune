
from acrcloud.recognizer import ACRCloudRecognizer
import re
import acrcloud.acrcloud_extr_tool as ACRext
import requests
import json
import lyricsgenius

from speech_recognition import Microphone
import speech_recognition as sr

#TODO: Work on more metadata extraction

def cleanString(string):
    # Gets rid of all special characters that may not be needed. Keeps commas and hyphens
    newString = re.sub('[^A-Za-z0-9,-_& ]+', '', string)
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
        self.lyric_access_token = "d7CUcPuyu-j9vUriI8yeTmp4PojoZqTp2iudYTf1jUtPHGLW352rDAKAjDmGUvEN"

    def getACRSongFingerprint(self, userfile):
        # @param userfile: audio file path

        songArray = list()
        returnsong = foundsong()

        # Get fingerprinted song string from ACR Cloud
        fingerprinted = self.acr.recognize_by_file(userfile, 0)
        print(fingerprinted)

        fingerprintJson = json.loads(fingerprinted)

        if 'Success' not in fingerprintJson['status']['msg']:
            print('ACRCloud: not found')
        else:
            songlist = (fingerprintJson['metadata']['music'][0])

            returnsong.set_title(cleanString(str(songlist['title'])))
            returnsong.set_artist((str(songlist['artists'])))
            returnsong.set_genre(cleanString(str(songlist['genres'])))
            returnsong.set_score(cleanString(str(songlist['score'])))
        return returnsong

    def getAudDFingerprint(self, userpath):
        files = {
            'file': open(userpath, 'rb'),
        }
        returnsong = foundsong()

        # Apparently this one is use for humming and such, but has low accuracy.
        # result = requests.post('https://api.audd.io/recognizeWithOffset/  ', data=self.data, files=files)
        result = requests.post('https://api.audd.io/ ', data=self.data, files=files)

        print(result.text)

        fingerprintJson = json.loads(result.text)

        if 'success' not in fingerprintJson['status'] or fingerprintJson['result'] is None:
            print('AudD: not found')
        else:
            songlist = (fingerprintJson['result'])

            returnsong.set_title(cleanString(str(songlist['title'])))
            returnsong.set_artist(cleanString(str(songlist['artist'])))
            try:
                returnsong.set_genre(cleanString(str(songlist['apple_music']['genreNames'])))
            except:
                print("No Apple Genres")

            returnsong.set_artist((str(songlist['apple_music']['artistName'])))
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
        print(fingerprintJson)

        if 'success' not in fingerprintJson['status'] or fingerprintJson['result'] is None:
            print('AudD Humming: not found')
        else:
            songlist = (fingerprintJson['result']['list'])
            for songs in range(len(songlist)):
                returnsong = foundsong()
                returnsong.set_title((str(songlist[songs]['title'])))
                returnsong.set_artist((str(songlist[songs]['artist'])))
                #returnsong.set_genre((songlist[songs]['genre']))
                returnsong.set_score(str(songlist[songs]['score']))

                songArray.append(returnsong)
        return songArray

    def get_lyrics(self,songtitle, songartist):
        genius = lyricsgenius.Genius(self.lyric_access_token)
        song = genius.search_song(title=songtitle, artist=songartist)
        lyrics = ''
        if song:
            lyrics = song.lyrics
        return lyrics

    def lyricSearch(self, songArray, userInput):
        # Take the lyrics and song array, loop and change string to find lyrics and all
        lyricSong = foundsong()
        print("UserInput: " + userInput)

        #Split UserArray and split it
        userInputArr = userInput.split(' ')
        for char in range(0,len(userInputArr)):
            userInputArr[char] = userInputArr[char].lower()

        foundSongFlag = False

        #Needs a base lyric array of 5 words or so
        if len(userInputArr) > 5:
            #Get each song in the array
            for x in range(0,len(songArray)):

                if foundSongFlag:
                    pass
                else:
                    print("Trying to Match with: " + songArray[x].title + " by " + songArray[x].artists)

                    # Get song title and artist in each array element
                    currTitle = songArray[x].title
                    currArtist = ''
                    if ',' in songArray[x].artists:
                        currArtist = songArray[x].artists[0: songArray[x].artists.index(',')]
                    else:
                        currArtist = songArray[x].artists

                    # Get the Lyrics
                    lyrics = self.get_lyrics(currTitle, currArtist)

                    # Edit and Split Lyrics so Headers are removed and lyrics are properly split
                    lyrics = lyrics.replace('\n', ' ')
                    lyricsArr = lyrics.split(' ')
                    for y in range(0, len(lyricsArr)):
                        if '(' in lyricsArr[y]:
                            index = 0
                            while ')' not in lyricsArr[y + index]:
                                lyricsArr[y + index] = ''
                                index += 1
                        if '[' in lyricsArr[y] or ']' in lyricsArr[y] or ')' in lyricsArr[y]:
                            lyricsArr[y] = ''
                        else:
                            lyricsArr[y] = lyricsArr[y].replace('?', '')
                            lyricsArr[y] = lyricsArr[y].replace('!', '')
                            lyricsArr[y] = lyricsArr[y].replace(',', '')
                            lyricsArr[y] = lyricsArr[y].lower()

                    # Get rid of all the blank char strings in lyrics array
                    lyricsArr = list(filter(None, lyricsArr))
                    # print(lyricsArr)

                    # Need to compare lyrics and userinput now
                    for z in range(0, len(lyricsArr)):
                        # Check to see if the first input matches with anything
                        if userInputArr[0] == lyricsArr[z] and not foundSongFlag:
                            counter = 1
                            for restOfTheInput in range(1, len(userInputArr)):
                                try:
                                    if userInputArr[restOfTheInput] == lyricsArr[z + restOfTheInput]:
                                        counter += 1
                                except:
                                    pass
                            if counter >= (len(userInputArr) * .5):
                                lyricSong.set_title(songArray[x].title)
                                lyricSong.set_artist(songArray[x].artists)
                                lyricSong.set_genre(songArray[x].genres)
                                lyricSong.set_score(songArray[x].score)
                                foundSongFlag = True;
                                print('Matched song with: ' + songArray[x].title + ' ' + songArray[x].artists)
                    if not foundSongFlag:
                        print("Song did not Match")

        if not foundSongFlag:
            print("No Songs have matched in the humming return")
        return lyricSong

    def searchFingerprintAll(self, userfile, userInput):

        #Weighted AudD first, then ACR, then humming
        audDfoundSong = self.getAudDFingerprint(userfile)
        ACRfoundSong = self.getACRSongFingerprint(userfile)
        hummingFingerprint = self.getHummingFingerprint(userfile)

        lyricSong = self.lyricSearch(hummingFingerprint, userInput)


        result = foundsong()
        if audDfoundSong.title:
            result.set_title(audDfoundSong.title)
            result.set_artist(audDfoundSong.artists)
            result.set_genre(audDfoundSong.genres)
            result.set_score(audDfoundSong.score)
        else:
            if ACRfoundSong.title:
                result.set_title(ACRfoundSong.title)
                result.set_artist(ACRfoundSong.artists)
                result.set_genre(ACRfoundSong.genres)
                result.set_score(ACRfoundSong.score)
            else:
                try:
                    if (lyricSong.title == ''):
                        result.set_title(hummingFingerprint[0].title)
                        result.set_artist(hummingFingerprint[0].artists)
                        result.set_genre(hummingFingerprint[0].genres)
                        result.set_score(hummingFingerprint[0].score)
                    else:
                        result.set_title(lyricSong.title)
                        result.set_artist(lyricSong.artists)
                        result.set_genre(lyricSong.genres)
                        result.set_score(lyricSong.score)
                except:
                    result.set_title('None')
                    result.set_artist('None')
                    result.set_genre('None')
                    result.set_score('None')
        return result










#   TESTING   ##################################################################################################################

'''
obj = FingerprintRequest()

file = r"C:\\Users\\2015d\\OneDrive\\Desktop\\.wav files\\pretender.wav"

with sr.AudioFile(file) as source:    # Load the file
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    data = r.record(source)
    recognized = r.recognize_google(data)


    lastTest = obj.searchFingerprintAll(file, recognized)

    print(lastTest.title)
    print(lastTest.artists)
    print(lastTest.genres)
    print(lastTest.score)

    pass
'''
'''
testSong = foundsong()
testSong.set_artist('Foo Fighters')
testSong.set_title('Pretender')

lyrics = obj.lyricSearchSong(testSong)
lyrics = lyrics.replace('\n', ' ')

print(lyrics.split(' '))
'''

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
hummingTest = obj.getHummingFingerprint(file)
try:
    print(hummingTest.title)
    print(hummingTest.artists)
    print(hummingTest.genres)
    print(hummingTest.score)
except:
    pass
    
'''
'''
lastTest = obj.searchFingerprintAll(file)
print(lastTest.title)
print(lastTest.artists)
print(lastTest.genres)
print(lastTest.score)
'''

