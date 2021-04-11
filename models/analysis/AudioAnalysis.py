"""
1. accept the user input rhythm recording
2. fetch DB information onset_frames <hashed string>, peak_frames<hashed string>, sr <int>
3. compare the user input with information from database
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
6. data processing: hash from db > bin > frame > timestamp > drop ambiguous > pattern -> compare function
"""

import librosa
import math
from models.Database import db, get_cursor
from models.Song import Song
import numpy as np

"""COMPARISON FUNCTIONS"""


# Purpose: for pair of beats that are too closer to each other that sounds like one beat to human ears, consider them
#          as one beat
# Status: clear
def drop_ambiguous(timestamp):
    result = [timestamp[0]]
    i = 1
    while i <= len(timestamp) - 1:
        if timestamp[i] - timestamp[i - 1] >= 0.08:
            result.append(timestamp[i])
        i += 1
    return result


# finds difference between every 2nd timestamp
def merge_beats(timestamps):
    new_times = []
    for x in range(len(timestamps) - 2):
        dif = timestamps[x + 2] - timestamps[x]
        new_times.append(dif)

    return new_times


# Purpose:  take in timestamp, return pattern
# Principle: process timestamp and get pattern by getting time differences between each beat
# Status: clear
def process_timestamp_diff(timestamp):
    beat_diff = []
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
    return beat_diff


# Purpose: take in timestamp, output pattern
# Principle: analyze timestamp by deviding each timestamp by avg beat_diff, beat_diff: time difference between one beat
#            to next one
# Status: clear, waiting for tests
def process_timestamp_ratio(timestamp):
    beat_diff_over_avg = []
    diff = 0
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        diff += temp
    avg_diff = diff / len(timestamp)
    for i in range(len(timestamp)):
        beat_diff_over_avg.append(timestamp[i] / avg_diff)
    return beat_diff_over_avg


# Purpose: Compare two ratio pattern and calculate matching rate
# Principle: if user_pattern[i] / song_pattern[i] is very close t 1, it is a match beat, record that result for
#            matching rate calculation
# Status: In progess, error range need more testing to determine
# Note: round both item to same decimal precision to compare?
def compare_ratio(user_pattern, song_pattern):
    mark = round(len(user_pattern) * 0.7)
    numOfHit = 0
    error = 0.2  # Working process
    j = 0
    match_rate = 0
    for i in range(len(song_pattern) - len(user_pattern)):

        while j < len(user_pattern):
            match_rate_this_beat = round(1 - (abs(1 - user_pattern[j] / song_pattern[i])), 4)
            if match_rate_this_beat >= 0.8:
                # print("It's a hit!")
                numOfHit += 1
                match_rate += match_rate_this_beat
                # print('Update match_rate: {}'.format(match_rate))
                i += 1
                j += 1
                break
            elif j < len(user_pattern) - 1:
                j += 1
            else:
                j = 0
                break

        # if numOfHit >= mark:
        #     return 1
    if numOfHit >= mark:
        return 1, round(match_rate / numOfHit, 4)
    else:
        return 0, round(match_rate / len(user_pattern), 4)


# Purpose: Split a song into three section as a list. Iterate through the list for compare, provide early exit if song
#          match in the first half.
#   section one: first half
#   Section two: Second half
#   Section three(enhanced section): from middle of first half to middle of second half, last section to run, make sure
#                                    no part is missed
# Principle: compare first half first, if not match, compare with second half, if both are not match, exit. If both have
#            some match, compare
#            the thitd section to ensure
# Status: Clear
# Note: Another approach to split the song?
def split_song(song_pattern):
    length = len(song_pattern)
    pattern_set = [song_pattern[0:(length / 2)], song_pattern[(length / 2):-1],
                   song_pattern[(length / 4):(length * 3 / 4)]]
    return pattern_set


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

# multi layer inputs: 1. compare seperately 2. combine different layers of the input and compare to the song
# split the song acccording to the user input.
# use hash to do comparison instead of timestamp
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

    for i in range(len(songSynced) - len(userSynced)):
        for j in range(len(userSynced)):
            if songSynced[j] - error <= userSynced[j] <= songSynced[j] + error:
                numOfHit += 1
        # print("# of hit : {}".format(numOfHit))
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
    for x in range(count_val):
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
    for val in range(0, len(db_tok)):
        frame_val = db_tok[val]
        # if blank flag
        if (frame_val == ""):
            if val != len(db_tok) - 1:
                bin_array.append(1)

        # if a custom flag
        elif (frame_val[0] == "."):
            custom_flag = frame_val[1:len(frame_val) - 1]
            print('customer flag:', custom_flag, "frame val:", frame_val, 'No.:', val)
            add_blank(bin_array, int(custom_flag))
            if val != len(db_tok) - 1:
                bin_array.append(1)

        # known flag
        else:
            char_val = int(valToCount(frame_val))
            add_blank(bin_array, char_val)

            if (val != len(db_tok) - 1):
                bin_array.append(1)

    return bin_array


def bin_to_frame(bin_array):
    frames = []
    track = 0
    offset = 0
    check = 0

    for bin in bin_array:
        if (bin == 0) and (check != len(bin_array) - 1):
            track += 1

        elif (bin == 1):
            frames.append(track + offset)
            offset += 1

        else:
            frames.append(track + offset + 1)
            offset += 1
        check += 1
    return frames


# process the recording based on peaks
def process_recording_peaks(userInput, peakFrames):
    # User input prep
    new_input = merge_beats(userInput)
    new_input_pattern = process_timestamp_ratio(new_input)
    # DB song prep
    timestamp = librosa.frames_to_time(peakFrames, sr=22050)
    timestamp = drop_ambiguous(timestamp)
    song_pattern = process_timestamp_ratio(timestamp)

    # ---Decision making---
    decision, matching_rate = compare_ratio(new_input_pattern, song_pattern)
    if decision == 1:
        print("we have a match!")
        return 1, matching_rate
    else:
        return 0, matching_rate


# process the recording in full
def process_recording(userInput, onsetFrames):
    # DB song prep
    songTimestamp = librosa.frames_to_time(onsetFrames, sr=22050)
    song_pattern = process_timestamp_ratio(songTimestamp)
    # user input prep
    input_pattern = process_timestamp_ratio(userInput)

    # compare user input and DB info
    # ---Decision making---
    decision, matching_rate = compare_ratio(input_pattern, song_pattern)
    if decision == 1:
        print("we have a match!")
        return 1, matching_rate
    else:
        return 0, matching_rate


# process the recording in full
def process_recording2(userInput, onsetFrames):
    # DB song prep
    songTimestamp = librosa.frames_to_time(onsetFrames, sr=22050)
    songTimestampSync = change_tempo(songTimestamp, 60)
    # user input prep
    input_pattern = get_pattern(change_tempo(userInput, 60))

    # compare user input and DB info
    # ---Decision making---
    decision, matching_rate = match_temposync(songTimestampSync, input_pattern)
    if decision == 1:
        print("we have a match!")
        return 1, matching_rate
    else:
        return 0, matching_rate


# chenge timestamp to fit specific tempo k, ex change the song to 60 bpm, k=60
def change_tempo(timestamp, k):
    original_tempo = get_tempo(timestamp)
    rate = original_tempo / k
    adjusted = [i * rate for i in timestamp]
    return adjusted


# get tempo from timestamp
def get_tempo(timestamp):
    ans = len(timestamp) * 60 / timestamp[-1]
    return ans


def get_pattern(timestamp):
    beat_diff = []
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
    return beat_diff


def compare_sync(song_timestamp, user_pattern):
    header = 0
    tail = 1
    error = 0.2
    hit = 0
    offset = 0
    for i in user_pattern:
        target = i + offset
        while (tail < len(song_timestamp)):
            beatlength = song_timestamp[tail] - song_timestamp[header]
            if target - error <= beatlength <= target + error:
                hit += 1
                header = tail
                tail += 1
                offset = 0
                break
            # if we pass the target, stimulate the target
            elif beatlength > target + error:
                offset += i
                break
            # keep moving until we find a beat or miss the target
            else:
                tail += 1
    return hit


#
def match_temposync(song_timestamp, user_pattern):
    mark = 0.7 * len(user_pattern)
    index_song_pattern = 0
    for i in range(len(song_timestamp)):
        hit = compare_sync(song_timestamp[i:], user_pattern)
        if  hit >= mark:
            return 1, hit/len(user_pattern)
    return 0, 0


class rhythmAnalysis:

    def __init__(self, userTaps=None, filterResults=None):
        if (userTaps != None):
            """
            TODO: merge input_perc and input_harm into one general input
            """

            if isinstance(userTaps[0], list):
                self.numOfAry = 2
            else:
                self.numOfAry = 1

            if self.numOfAry == 1:
                self.user_input = userTaps
            if self.numOfAry == 2:
                self.user_input_perc = userTaps[0]
                self.user_input_harm = userTaps[1]
            # print('array dimension:', self.numOfAry)
        if (filterResults != None):
            self.filter_results = filterResults

    """
    FUNCTION TO COMPARE THE PEAKS OF THE USER INPUT TO THE DB VALUE
    """

    def onset_peak_func(self):
        print('-----------------------------------------------------user input:', self.user_input)
        song_results = []
        db_results = []

        if self.filter_results != None and len(self.filter_results) > 0:
            filter_ids = []
            for track in self.filter_results:
                filter_ids.append(track.id)
            db_results = Song.get_by_ids(filter_ids)

        else:
            # fetch all results and save in song_data list
            db_results = Song.get_all()

        # for loop to go through the song_data
        # for track in db_results:
        index = 0
        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song is:', db_track.id)
            peak_array = unhash_array(db_track.peak_hash)
            onset_array = unhash_array(db_track.onset_hash)
            # percussive_array = unhash_array(db_track.perc_hash)
            # harmonic_array = unhash_array(db_track.harm_hash)

            """
            convert binary array to frames
            """
            onset_frames = bin_to_frame(onset_array)
            peak_frames = bin_to_frame(peak_array)
            # percussive_frames = bin_to_frame(percussive_array)
            # harmonic_frames = bin_to_frame(harmonic_array)

            """
            compare with the user input
            """
            match_peak, matching_rate_peak = process_recording2(self.user_input, peak_frames)
            match_onset, matching_rate_onset = process_recording2(self.user_input, onset_frames)
            # match_percussive, matching_rate_percussive = process_recording(self.user_input_percussive, percussive_frames)
            # match_harmonic, matching_rate_harmonic = process_recording(self.user_input_harmonic, harmonic_frames)

            matching_rate = (matching_rate_onset + matching_rate_peak) / 2
            max = 0
            print(matching_rate)
            if (match_peak or match_onset):
                if (matching_rate > .7):
                    song_results.append({"song": db_track,
                                         "percent_match": matching_rate})
                    max += 1
            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results

    def onset_peak_func_hp(self):
        song_results = []
        db_results = []
        if self.filter_results != None and len(self.filter_results) > 0:
            filter_ids = []
            for track in self.filter_results:
                filter_ids.append(track.id)
            db_results = Song.get_by_ids(filter_ids)

        else:
            # fetch all results and save in song_data list
            db_results = Song.get_all()

        # for loop to go through the song_data
        # for track in db_results:
        index = 0
        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song id: ', db_track.id)

            # if user did not tap to perc, use harm array to match
            if self.user_input_perc[0] == 0 and len(self.user_input_perc) == 1:
                # print('user did not tap to perc')
                match_percussive = 0
                matching_rate_percussive = 0
            else:
                percussive_array = unhash_array(db_track.perc_hash)
                percussive_frames = bin_to_frame(percussive_array)
                match_percussive, matching_rate_percussive = process_recording2(self.user_input_perc, percussive_frames)

            # if user did not tap to harm, user perc array to match
            if self.user_input_harm[0] == 0 and len(self.user_input_harm) == 1:
                # print('user did not tap to harm')
                match_harmonic = 0
                matching_rate_harmonic = 0
            else:
                harmonic_array = unhash_array(db_track.harm_hash)
                harmonic_frames = bin_to_frame(harmonic_array)
                match_harmonic, matching_rate_harmonic = process_recording2(self.user_input_harm, harmonic_frames)

            # decide matching rate
            # if user only tap to harm or perc, don't let 0 matching rate effect final matching rate
            if matching_rate_harmonic == 0 or matching_rate_percussive == 0:
                if matching_rate_harmonic == 0:
                    matching_rate = matching_rate_percussive
                else:
                    matching_rate = matching_rate_harmonic
            else:
                matching_rate = (matching_rate_harmonic + matching_rate_percussive) / 2
            max = 0
            print(matching_rate)
            if match_percussive or match_harmonic:
                if matching_rate > .7:
                    song_results.append({"song": db_track,
                                         "percent_match": matching_rate})
                    max += 1
            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results

    def sync_func(self):
        song_results = []
        db_results = []
        if self.filter_results != None and len(self.filter_results) > 0:
            filter_ids = []
            for track in self.filter_results:
                filter_ids.append(track.id)
            db_results = Song.get_by_ids(filter_ids)

        else:
            # fetch all results and save in song_data list
            db_results = Song.get_all()

        # for loop to go through the song_data
        # for track in db_results:
        index = 0
        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song id: ', db_track.id)

            # if user did not tap to perc, use harm array to match
            if self.user_input_perc[0] == 0 and len(self.user_input_perc) == 1:
                # print('user did not tap to perc')
                match_percussive = 0
                matching_rate_percussive = 0
            else:
                percussive_array = unhash_array(db_track.perc_hash)
                percussive_frames = bin_to_frame(percussive_array)
                match_percussive, matching_rate_percussive = process_recording2(self.user_input_perc, percussive_frames)

            #if user did not tap to harm, user perc array to match
            if self.user_input_harm[0] == 0 and len(self.user_input_harm) == 1:
                # print('user did not tap to harm')
                match_harmonic = 0
                matching_rate_harmonic = 0
            else:
                harmonic_array = unhash_array(db_track.harm_hash)
                harmonic_frames = bin_to_frame(harmonic_array)
                match_harmonic, matching_rate_harmonic = process_recording2(self.user_input_harm, harmonic_frames)

            #decide matching rate
            #if user only tap to harm or perc, don't let 0 matching rate effect final matching rate
            if matching_rate_harmonic == 0 or matching_rate_percussive == 0:
                if matching_rate_harmonic == 0:
                    matching_rate = matching_rate_percussive
                else:
                    matching_rate = matching_rate_harmonic
            else:
                matching_rate = (matching_rate_harmonic + matching_rate_percussive) / 2
            max = 0
            print(matching_rate)
            if match_percussive or match_harmonic:
                if matching_rate > .7:
                    song_results.append({"song": db_track,
                                         "percent_match": matching_rate})
                    max += 1
            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results
