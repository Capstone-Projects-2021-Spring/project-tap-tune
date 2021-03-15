"""
1. accept the user input rhythm recording
2. fetch DB information onset_frames <hashed string>, peak_frames<hashed string>, sr <int>
3. compare the user iput with information from database
4. append the songs labeled as matches to a list of results
    results = [
                {
                    title: *title,
                    artist: *artis,
                    genres: *genres
                }
            ]

    results.append( {"title" : *title, "artist", *artist, "genres":*genre} )
5. Return the song results to use in the Filtering
"""

import librosa
import math
from models.Database import db, get_cursor

"""COMPARISON FUNCTIONS"""
# finds difference between every 2nd timestamp
def mergeBeats(timestamps):
    new_times = []
    for x in range(len(timestamps)-2):
        dif = timestamps[x+2] - timestamps[x]
        new_times.append(dif)

    return new_times

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

# compare input array to song
# find out if the userPattern[a1,a2,a3...] can be found in the songPattern[s1,s2,s3...]
# a multiple C meaning the how much faster/slower userPattern is to songPattern: a1= c*s1, a2=c*s2......
# a pattern note is a match if the error after multiplying c is smaller than XX
# return 1, meaning it is a match if more than XX%(70%) of the pattern note is matched
def compare(userPattern, songPattern):
    # synchronize two pattern
    base = min(min(userPattern), min(songPattern)) # use the min in two pattern as base for synchronization
    userSynced = synchronize(userPattern, base)
    songSynced = synchronize(songPattern, base)

    # error range
    error = 0.5

    # how many notes need to match to pass
    mark = math.floor(len(userSynced) * 0.7)

    # keep track of how many match appears
    numOfHit = 0

    for i in range(len(songSynced) - len(userSynced)):
        for j in range(len(userSynced)):
            if songSynced[j] - error <= userSynced[j] <= songSynced[j] + error:
                numOfHit += 1
        print("# of hit : {}".format(numOfHit))
        if numOfHit >= mark:
            return 1
        else:
            numOfHit = 0
    print("max # of hit : {}".format(numOfHit))
    if numOfHit >= mark:
        return 1
    else:
        return 0

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
    print(db_string)
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

    print("****************SHOULD BE Length of Frames************************")
    print(val)
    print(len(bin_array))

    return bin_array

# process the recording based on peaks
def processRecoringPeaks(userInput, peakFrames):
    # DB song prep
    output1, output2 = process_timestamp2(peakFrames)

    # User input prep
    new_input = mergeBeats(userInput)
    framestoTime = librosa.frames_to_time(output1, sr=22050)

    # ---Decision making---
    if compare(new_input, framestoTime) == 1:
        print("we have a match!")
    else:
        print("no match found")


class rhythmAnalysis:

    def __innit__(self, userTaps = None):
        print(userTaps)
        if(userTaps != None):
            self.user_input = userTaps
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

        """
        convert peak_hash to binary array
        """
        bin_array = unhash_array(db_results[1]["peak_hash"])
        print(bin_array)

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
            title = db_results[0]["title"]
            artist = db_results[0]["artist"]
            genres = db_results[0]["genres"]

            song_results.append( {"title": title, "artist": artist, "genres": genres} )

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

        """
        convert onset_hash to binary array
        """
        bin_array = unhash_array(db_results[1]["onset_hash"])
        print(bin_array)

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
            title = db_results[0]["title"]
            artist = db_results[0]["artist"]
            genres = db_results[0]["genres"]

            song_results.append( {"title": title, "artist": artist, "genres": genres} )
