
from acrcloud.recognizer import ACRCloudRecognizer
import re
import acrcloud.acrcloud_extr_tool as ACRext
import requests
import json
import speech_recognition as sr
import lyricsgenius

def cleanString(string):
    # Gets rid of all special characters that may not be needed. Keeps commas and hyphens
    newString = re.sub('[^A-Za-z0-9,-_& ]+', '', string)
    newerString = re.sub(r'[\[\]]', '', newString)

    return newerString

# Song object for returning the song found from ACRCloud
# Can Add attributes if extra metadata extraction is needed
class foundsong:
    def __init__(self):
        self.title = ""
        self.artists = ""
        self.genres = ""
        self.score = ""

        self.timeCode = ""

    def set_title(self, title):
        self.title = title

    def set_artist(self, artists):
        self.artists = artists

    def set_genre(self, genres):
        self.genres = genres

    def set_score(self, score):
        self.score = score

    # Only for auto database input
    def set_timeCode(self, timeCode):
        self.timeCode = timeCode


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
            'api_token': '12134706180f4b0c35e751471547336b'
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
            returnsong.set_artist((str(songlist['artists'][0]['name'])))
            try:
                returnsong.set_genre(cleanString(str(songlist['genres'])))
            except:
                pass
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
            returnsong.set_timeCode(str(songlist['timecode']))
            try:
                returnsong.set_genre(cleanString(str(songlist['apple_music']['genreNames'])))
                returnsong.set_artist((str(songlist['apple_music']['artistName'])))
            except:
                print("No Apple Genres")

            # returnsong.set_score(cleanString(str(songlist['score'])))

        files['file'].close()
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
            if 'error' in fingerprintJson['status']:
                print('Error with AudD Service found')
                returnsong = foundsong()
                returnsong.set_title("There was an Error with the Service")
                songArray.append(returnsong)
            else:
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

        files['file'].close()
        return songArray

    def lyricSearch(self, songArray, userInput, leniency):

        def get_lyrics(songtitle, songartist):
            genius = lyricsgenius.Genius(self.lyric_access_token)
            song = genius.search_song(title=songtitle, artist=songartist)
            lyrics = ''
            if song:
                lyrics = song.lyrics
            return lyrics

        # Inner Function to clear special characters for each word
        def clearSyntax(string):
            string = string.replace('?', '')
            string = string.replace('!', '')
            string = string.replace(',', '')
            string = string.replace('.', '')
            string = string.lower()
            return string

        # Take the lyrics and song array, loop and change string to find lyrics and all
        lyricSong = foundsong()
        print("UserInput: " + userInput)

        #Split UserArray
        userInputArr = userInput.split(' ')
        for char in range(0, len(userInputArr)):
            userInputArr[char] = clearSyntax(userInputArr[char])

        loop = 5
        if songArray is not None and len(songArray) < loop:
            loop = len(songArray)

        foundSongFlag = False

        #Needs a base lyric array of at least 5 words
        if len(userInputArr) > 5:
            #Get each song in the array
            for x in range(0, loop):

                # Goes in top to bottom order. If the song is found, pass the rest of the search
                if foundSongFlag:
                    pass
                else:
                    #print("Trying to Match with: " + songArray[x].title + " by " + songArray[x].artists + "at " + str(leniency) + " leniency")

                    # Get song title and artist in each array element
                    currTitle = songArray[x].title
                    currArtist = ''
                    if ',' in songArray[x].artists:
                        currArtist = songArray[x].artists[0: songArray[x].artists.index(',')]
                    else:
                        currArtist = songArray[x].artists

                    # Get the Lyrics from Genius API
                    lyrics = get_lyrics(currTitle, currArtist)

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
                            lyricsArr[y] = clearSyntax(lyricsArr[y])

                    # Get rid of all the blank char strings in lyrics array
                    lyricsArr = list(filter(None, lyricsArr))

                    # compares each word between lyrics and userInput Lyrics now.
                    for z in range(0, len(lyricsArr)):
                        # Check to see if the first input matches with anything if yes, check the rest of userInput
                        if userInputArr[0] == lyricsArr[z] and not foundSongFlag:

                            # Some variables initialized for the check
                            counter = 1             # Counter for how many words matched
                            inputOffset = 0         # Sync variable for userInput
                            lyricOffset = 0         # Sync Variable for Lyrics
                            restOfTheInput = 1      # Iterator for each index in userInput array

                            # Start comparison for the entire songlyrics. Stops if song is found
                            while (restOfTheInput + inputOffset) < len(userInputArr) and not foundSongFlag:
                                # print('comparing: ' + userInputArr[restOfTheInput + inputOffset] + '\t' + lyricsArr[z + restOfTheInput + lyricOffset])

                                try:
                                    if userInputArr[restOfTheInput+inputOffset] == lyricsArr[z + restOfTheInput + lyricOffset]:
                                        counter += 1
                                    else:
                                        # print('Not matched. Trying Extra Comparisons')

                                        lyricOffsetFlag = False
                                        inputOffsetFlag = False

                                        # Checks if User word is upcoming in the lyrics. If so, match and sync the userInput to that part in the Lyrics
                                        for a in range(0, 3):
                                            if not lyricOffsetFlag:
                                                try:
                                                    # print('comparing: ' + userInputArr[restOfTheInput + inputOffset] + '\t' + lyricsArr[z + restOfTheInput + a + lyricOffset])
                                                    if userInputArr[restOfTheInput + inputOffset] == lyricsArr[z + restOfTheInput + a + lyricOffset]:
                                                        lyricOffset += a
                                                        lyricOffsetFlag = True
                                                        counter += 1
                                                except IndexError:
                                                    # print('Out of Bounds. Proceeding')
                                                    pass

                                        # If the userInput word was not found, see if maybe the Lyric is in the upcomming UserInput. if so, match and sync
                                        if not lyricOffsetFlag:
                                            for b in range(0, 3):
                                                if not inputOffsetFlag:
                                                    try:
                                                        # print('comparing: ' + lyricsArr[z + restOfTheInput + lyricOffset] + '\t' + userInputArr[restOfTheInput + b + inputOffset])
                                                        if lyricsArr[z + restOfTheInput + lyricOffset] == userInputArr[restOfTheInput + b + inputOffset]:
                                                            inputOffset += b
                                                            inputOffsetFlag = True
                                                            counter += 1
                                                    except IndexError:
                                                        # print('Out of Bounds. Proceeding')
                                                        pass
                                    ''' Logging print statements
                                    print('Input Offset: ' + str(inputOffset))
                                    print('Lyric Offset: ' + str(lyricOffset))
                                    print('Counter : ' + str(counter))

                                    print('Moving to next comparison')
                                    print('\n')
                                    '''

                                    restOfTheInput += 1

                                    # If there is a 60% match in the lyrics, then the song is deemed "found"
                                    if counter >= (len(userInputArr) * leniency):
                                        print(str(counter) + "/" + str(len(userInputArr)) + '=' + str(counter / len(userInputArr)))
                                        foundSongFlag = True
                                except:
                                    pass

                            if foundSongFlag:
                                lyricSong.set_title(songArray[x].title)
                                lyricSong.set_artist(songArray[x].artists)
                                lyricSong.set_genre(songArray[x].genres)
                                lyricSong.set_score(100)
                                print('Matched song with: ' + songArray[x].title + ' ' + songArray[x].artists)
                    if not foundSongFlag:
                        print("Song did not Match")

        if not foundSongFlag:
            print("No Songs have matched in the humming return")
        return lyricSong

    def getSongFromLyrics(self, userInput):
        match = 0
        genius = lyricsgenius.Genius(self.lyric_access_token)
        result_data = []

        if userInput == '':
            print("User Input was empty")
            pass
        else:
            try:
                # makes request to genius API and wrapper to search through lyrics
                request = genius.search_lyrics(userInput, per_page=50, page=(1))
                """PARSE DATA FOR ARTIST NAME AND SONG TITLE"""
                for hit in request['sections'][0]['hits']:
                    artist_name = hit['result']['primary_artist']['name']
                    song_title = hit['result']['title']

                    song = foundsong()
                    song.set_title(song_title)
                    song.set_artist(artist_name)

                    result_data.append(song)


            except Exception as e:
                print(e)
            '''
            for x in range(len(result_data)):
                print(result_data[x].title)
                print(result_data[x].artists)
                print('')
            '''
            return result_data


    def searchFingerprintAll(self, userfile, userInput):

        #Weighted AudD first, then ACR, then humming
        audDfoundSong = self.getAudDFingerprint(userfile)
        ACRfoundSong = self.getACRSongFingerprint(userfile)
        hummingFingerprint = self.getHummingFingerprint(userfile)

        if len(hummingFingerprint) > 0:
            if hummingFingerprint[0].title != "There was an Error with the Service":
                lyricSong = self.lyricSearch(hummingFingerprint, userInput, .6)
                songFromLyrics = self.lyricSearch(self.getSongFromLyrics(userInput), userInput, .6)
            else:
                lyricSong = hummingFingerprint[0]
                songFromLyrics = foundsong()

            if lyricSong.title != '' and songFromLyrics.title != '':
                songCompare = []
                songCompare.append(lyricSong)
                songCompare.append(songFromLyrics)
                threshold = .9

                lyricSong = self.lyricSearch(songCompare, userInput, threshold)
                while lyricSong.title == '':
                    threshold -= .05
                    if threshold < .5: #Theoretically it shouldn't reach this point at all but it's a failsafe
                        break;

                    lyricSong = self.lyricSearch(songCompare, userInput, threshold)


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
                    if lyricSong.title == '' and songFromLyrics.title != '':
                        result.set_title(songFromLyrics.title)
                        result.set_artist(songFromLyrics.artists)
                        result.set_genre(songFromLyrics.genres)
                        result.set_score(songFromLyrics.score)
                    elif lyricSong.title != '' and (songFromLyrics.title == '' or songFromLyrics.title != ''):
                        result.set_title(lyricSong.title)
                        result.set_artist(lyricSong.artists)
                        result.set_genre(lyricSong.genres)
                        result.set_score(lyricSong.score)
                    else:
                        result.set_title(hummingFingerprint[0].title)
                        result.set_artist(hummingFingerprint[0].artists)
                        result.set_genre(hummingFingerprint[0].genres)
                        result.set_score(hummingFingerprint[0].score)
                except:
                    result.set_title('None')
                    result.set_artist('None')
                    result.set_genre('None')
                    result.set_score('None')
        return result


#   TESTING   ##################################################################################################################

'''
obj = FingerprintRequest()

file = r"C:\\Users\\2015d\\OneDrive\\Desktop\\.wav files\\untitled.wav"

with sr.AudioFile(file) as source:    # Load the file
    r = sr.Recognizer()
    r.energy_threshold = 4000
    r.dynamic_energy_threshold = True
    data = r.record(source)
    try:
        recognized = r.recognize_google(data, key='AIzaSyAEi5c2CU_gf3RsJGv6UVt1EqnylEn6mvc')
    except:
        recognized = ''

    lastTest = obj.searchFingerprintAll(file, recognized)

    print(lastTest.title)
    print(lastTest.artists)
    print(lastTest.genres)
    print(lastTest.score)
    print(lastTest.timeCode)

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

