"""
1. accept the user input rhythm recording
2. fetch DB information onset_frames <hashed string>, peak_frames<hashed string>, sr <int>
3. compare the user iput with information from database
4. append the songs labeled as matches to a list of results
    results = [
                {
                    title: *title,
                    artist: *artist,
                    genres: *genres
                }
            ]

    results.append( {"title" : *title, "artist", *artist, "genres":*genre} )
5. Return the song results to use in the Filtering
"""

import librosa
import math
from acrcloud.recognizer import ACRCloudRecognizer
import re
from models.Database import db, get_cursor


def dupCheck(self, dict, target):
    for track in dict:
        if target in track:
            pass
        else:
            return False
    return True

"""COMPARISON FUNCTIONS"""
# finds difference between every 2nd timestamp
def mergeBeats(timestamps):
    new_times = []
    for x in range(len(timestamps)-2):
        dif = timestamps[x+2] - timestamps[x]
        new_times.append(dif)

    return new_times

"""DEPRECATED"""
# Second approach to process song timestamp array for pattern
# 1. compute time differences between each beat
# 2. get even time difference
# 3. time difference/avg time difference as relative difference(pattern)
# 4. returns two patterns, first one: time_diff second one: time_diff/avg_diff
def process_timestamp2(timestamp):
    beat_diff = []
    beat_diff_over_avg = []
    diff = 0
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
        diff += temp
    avg_diff = diff / len(timestamp)
    for i in range(len(timestamp)):
        beat_diff_over_avg.append(timestamp[i] / avg_diff)
    return beat_diff, beat_diff_over_avg

# function to synchronize two pattern
def synchronize(originalPattern, base):
    syncedPattern = []
    for i in originalPattern:
        syncedPattern.append(i / base)
    return syncedPattern

"""MODIFIED"""
# compare input array to song
# find out if the userPattern[a1,a2,a3...] can be found in the songPattern[s1,s2,s3...]
# a multiple C meaning the how much faster/slower userPattern is to songPattern: a1= c*s1, a2=c*s2......
# a pattern note is a match if the error after multiplying c is smaller than XX
# return 1, meaning it is a match if more than XX%(70%) of the pattern note is matched
def compare(userPattern, songPattern):
    # synchronize two pattern
    base = min(min(userPattern), min(songPattern))  # use the min in two pattern as base for synchronization
    userSynced = synchronize(userPattern, base)
    songSynced = synchronize(songPattern, base)

    # error range
    error = 0.5

    # how many notes need to match to pass
    mark = math.floor(len(userSynced) * 0.7)

    # keep track of how many match appears
    numOfHit = 0
    checkedPattern = 0
    matchAVG = 0

    # match res should accept the matchAVG
    matchRes = 0

    for i in range(len(songSynced) - len(userSynced)):
        checkedPattern += 1
        for j in range(len(userSynced)):
            if songSynced[j] - error <= userSynced[j] <= songSynced[j] + error:
                numOfHit += 1
        # print("# of hit : {}".format(numOfHit))

        # calculates the match percentage of the one pattern check
        # adds the match percentage to the average of previous match percentages
        match = numOfHit / len(userPattern)
        match *= 100
        matchAVG = (matchAVG + match) / checkedPattern
        if numOfHit >= mark:
            return 1, (matchAVG)
        else:
            numOfHit = 0
    # print("max # of hit : {}".format(numOfHit))
    if numOfHit >= mark:
        return 1, (matchAVG)
    else:
        return 0, (matchAVG)

"""CONVERSION FUNCTIONS"""

# adds the blanks for unhashing the db value
# used to add 0 based on the flags
def add_blank(bin_array, count_val):
    for x in range (count_val):
        bin_array.append(0)

# converts the val flag into the number of 0's
def valToCount(frame_val):
    dict = {
        0: "*",
        1: "0",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "A",
        11: "B",
        12: "C",
        13: "D",
        14: "E",
        15: "F",
        16: "G",
        17: "H",
        18: "I",
        19: "J",
        20: "K",
        21: "L",
        22: "M",
        23: "N",
        24: "O",
        25: "P",
        26: "Q",
        27: "R",
        28: "S",
        29: "T",
        30: "U",
        31: "V",
        32: "W",
        33: "X",
        34: "Y",
        35: "Z"
    }

    key_list = list(dict.keys())
    val_list = list(dict.values())

    return key_list[val_list.index(frame_val)]

# takes in the db value and unhashes it to form a binary array
def unhash_array(db_string):
    db_tok = db_string.split("*")
    bin_array = []
    char_val = ""
    for val in range (0, len(db_tok)):
        frame_val = db_tok[val]
        # if blank flag
        if(frame_val == ""):
            if val != len(db_tok)-1:
                bin_array.append(1)

        # if a custom flag
        elif(frame_val[0] == "."):
            custom_flag = frame_val[1:len(frame_val)-1]
            add_blank(bin_array, int(custom_flag))
            if val != len(db_tok) - 1:
                bin_array.append(1)

        #known flag
        else:
            char_val = int(valToCount(frame_val))
            add_blank(bin_array, char_val)

            if(val != len(db_tok)-1):
                bin_array.append(1)

    return bin_array

# process the recording based on peaks
def processRecoringPeaks(userInput, peakFrames):
    # DB song prep
    output1, output2 = process_timestamp2(peakFrames)

    # User input prep
    new_input = mergeBeats(userInput)
    framestoTime = librosa.frames_to_time(output1, sr=22050)

    bool, match_res = compare(new_input, framestoTime)

    # print("*************MATCH AVERAGE****************")
    # print(match_res)

    # ---Decision making---
    if bool == 1:
        print("we have a match!")
        return 1
    else:
        print("no match found")
        return 0

# process the recording in full
def processRecoring(userInput, onsetFrames):
    # DB song prep
    songTimestamp = librosa.frames_to_time(onsetFrames, sr=22050)
    songP1, songP2 = process_timestamp2(songTimestamp)
    # user input prep
    inputP1, inputP2 = process_timestamp2(userInput)

    # compare user input and DB info
    # ---Decision making---
    bool, match_res = compare(inputP1, songP1)

    # print("*************MATCH AVERAGE****************")
    # print(match_res)
    # ---Decision making---
    if bool == 1:
        print("we have a match!")
        return 1
    else:
        print("no match found")
        return 0

class rhythmAnalysis:

    def __init__(self, userTaps=None, filterResults=None):
        print(userTaps)
        if(userTaps != None):
            self.user_input = userTaps
        if(filterResults != None):
            self.filter_results = filterResults
    """
    FUNCTION TO COMPARE THE PEAKS OF THE USER INPUT TO THE DB VALUE
    """
    def peak_func(self):
        song_results = []

        # retrieves cursor from Database.py
        cursor = get_cursor()
        cursor.execute('SELECT title, artist, genre, peak_hash FROM song')
        # fetch al results and save in song_data list

        """GO THROUGH DB DATA"""
        song_data = cursor.fetchall()
        db_results = []
        for track in song_data:
            title = track["title"]
            artist = track['artist']
            genres = track["genre"]
            peak_hash = track['peak_hash']

            db_results.append( {"title": title, "artist": artist, "genres": genres, "peak_hash": peak_hash})

        # for loop to go through the song_data
        # for track in db_results:
        index = 0
        for db_track in db_results:
            """
            convert peak_hash to binary array
            """
            print("**************SONG CHECK*******************")
            print(db_track["title"])
            bin_array = unhash_array(db_track["peak_hash"])

            """
            convert binary array to frames
            """
            # frames from bin
            res_frames = []
            track = 0
            offset = 0
            check = 0

            for bin in bin_array:
                if (bin == 0) and (check != len(bin_array) - 1):
                    track += 1

                elif (bin == 1):
                    res_frames.append(track + offset)
                    offset += 1

                else:
                    res_frames.append(track + offset + 1)
                    offset += 1
                check += 1

            print(res_frames)
            """
            compare with the user input
            """
            match = processRecoringPeaks(self.user_input, res_frames)

            if (match):
                title = db_results[index]["title"]
                artist = db_results[index]["artist"]
                genres = db_results[index]["genres"]

                song_results.append( {"title": title, "artist": artist, "genres": genres} )
            index += 1


        if(len(song_results) < 1):
            return None
        else:
            return song_results

    def onset_func(self):
        song_results = []

        # retrieves cursor from Database.py
        cursor = get_cursor()
        cursor.execute('SELECT title, artist, genre, onset_hash FROM song')
        # fetch all results and save in song_data list

        """GO THROUGH DB DATA"""
        song_data = cursor.fetchall()
        db_results = []
        for track in song_data:
            title = track["title"]
            artist = track['artist']
            genres = track["genre"]
            onset_hash = track['onset_hash']

            db_results.append( {"title": title, "artist": artist, "genres": genres, "onset_hash": onset_hash})

        # for loop to go through the song_data
        # for track in db_results:
        index = 0
        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            bin_array = unhash_array(db_track["onset_hash"])
            print(db_track)

            """
            convert binary array to frames
            """
            # frames from bin
            res_frames = []
            track = 0
            offset = 0
            check = 0

            for bin in bin_array:
                if (bin == 0) and (check != len(bin_array) - 1):
                    track += 1

                elif (bin == 1):
                    res_frames.append(track + offset)
                    offset += 1

                else:
                    res_frames.append(track + offset + 1)
                    offset += 1
                check += 1

            """
            compare with the user input
            """
            match = processRecoring(self.user_input, res_frames)

            if (match):
                title = db_results[0]["title"]
                artist = db_results[0]["artist"]
                genres = db_results[0]["genres"]

                song_results.append( {"title": title, "artist": artist, "genres": genres} )

                title = db_results[index]["title"]
                artist = db_results[index]["artist"]
                genres = db_results[index]["genres"]

                song_results.append( {"title": title, "artist": artist, "genres": genres} )
            index += 1

        if (len(song_results) < 1):
            return None
        else:
            return song_results

    def onset_peak_func(self):
        song_results = []
# try catch here
        try:
            # retrieves cursor from Database.py
            cursor = get_cursor()
            cursor.execute('SELECT title, artist, genre, onset_hash, peak_hash FROM song')
            # fetch all results and save in song_data list

            """GO THROUGH DB DATA"""
            song_data = cursor.fetchall()
            db_results = []
            for track in song_data:
                title = track["title"]
                artist = track['artist']
                genres = track["genre"]
                onset_hash = track['onset_hash']
                peak_hash = track['peak_hash']

                db_results.append({"title": title, "artist": artist, "genres": genres, "onset_hash": onset_hash, "peak_hash": peak_hash})

            # for loop to go through the song_data
            # for track in db_results:
            index = 0
            for db_track in db_results:
                """
                convert onset_hash to binary array
                """
                peak_array = unhash_array(db_track["peak_hash"])
                onset_array = unhash_array(db_track["onset_hash"])
                print(db_track)

                """
                convert binary array to frames
                """
                # frames from bin
                onset_frames = []
                track = 0
                offset = 0
                check = 0

                for bin in onset_array:
                    if (bin == 0) and (check != len(peak_array) - 1):
                        track += 1

                    elif (bin == 1):
                        onset_frames.append(track + offset)
                        offset += 1

                    else:
                        onset_frames.append(track + offset + 1)
                        offset += 1
                    check += 1

                peak_frames = []
                track = 0
                offset = 0
                check = 0
                for bin in peak_array:
                    if (bin == 0) and (check != len(peak_array) - 1):
                        track += 1

                    elif (bin == 1):
                        peak_frames.append(track + offset)
                        offset += 1

                    else:
                        peak_frames.append(track + offset + 1)
                        offset += 1
                    check += 1


                """
                compare with the user input
                """
                match = processRecoringPeaks(self.user_input, peak_frames)
                match2 = processRecoring(self.user_input, onset_frames)


                if (match or match2):
                    title = db_results[index]["title"]
                    artist = db_results[index]["artist"]
                    genres = db_results[index]["genres"]

                    song_results.append({"title": title, "artist": artist, "genres": genres})
                index += 1
            if(self.filter_results):
                # if there is a list of songs from filtering
                # compare the filter_results list to song_results
                final_result = []
                for filter_track in self.filter_results:
                    for analysis_track in song_results:
                        if(filter_track["title"] == analysis_track["title"]):
                            if(dupCheck(final_result, analysis_track["title"])):
                                final_result.append(analysis_track)

            if (len(song_results) < 1):
                return None
            else:
                return song_results
        except Exception as e:
            print(e)



'''
Start of Melody Analysis
'''
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

class foundsong:
    def __init__(self):
        self.title = ""
        self.artists = ""
        self.genres = ""

        # Only for auto database input
        self.path = ""

    def set_title(self, title):
        self.title = title

    def set_artist(self, artists):
        self.artists = artists

    def set_genre(self, genres):
        self.genres = genres

    # Only for auto database input
    def set_path(self, path):
        self.path = path

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
        # print(fingerprinted)

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
                # print(substr)

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
