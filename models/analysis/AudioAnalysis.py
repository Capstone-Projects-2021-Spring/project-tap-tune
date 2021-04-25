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


# process the recording in full, userInput = user's timestamp sync then get pattern
def process_recording2(userInput, songTimestamp):
    # DB song prep
    # songTimestamp = librosa.frames_to_time(onsetFrames, sr=22050)
    # songTimestampSync = change_tempo(songTimestamp, 60)

    # compare user input and DB info
    # ---Decision making---
    decision, matching_rate, header, tail = match_temposync(songTimestamp, userInput)
    if decision == 1:
        print("we have a match!")
        return 1, matching_rate, header, tail
    else:
        return 0, matching_rate, 0, 0


# chenge timestamp to fit specific tempo k, ex change the song to 60 bpm, k=60
def change_tempo(timestamp, k):
    if k <= 0:
        print('tempo cant be equal or smaller than 0')
        return []
    else:
        original_tempo = get_tempo(timestamp)
        try:
            rate = original_tempo / k
            adjusted = [i * rate for i in timestamp]
            return adjusted
        except TypeError:
            print('NoneType values')
            return []


# get tempo from timestamp
def get_tempo(timestamp):
    try:
        ans = len(timestamp) * 60 / timestamp[-1]
        return ans
    except ZeroDivisionError:

        print('0s in the timestamp list')
        return 0
    except IndexError:
        print('list is empty!')
        return 0
    except TypeError:
        print('data type of input error')
        return 0



def get_pattern(timestamp):
    beat_diff = []
    try:
        for i in range(len(timestamp) - 1):
            temp = timestamp[i + 1] - timestamp[i]
            if temp>0:
                beat_diff.append(temp)
    except TypeError:
        print('input data type error')
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
    return hit, tail


#
def match_temposync(song_timestamp, user_pattern):
    mark = 0.7 * len(user_pattern)
    index_song_pattern = 0
    for i in range(len(song_timestamp)):
        hit, tail = compare_sync(song_timestamp[i:], user_pattern)
        if hit >= mark:
            return 1, ((hit / tail) + hit / len(user_pattern)) / 2, i, i + tail
    return 0, 0, 0, 0


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


# opposite of valToCount
def countToVal(count):
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

    if count in dict.keys():
        return dict[count]

    else:
        dict.update({count: str(count)})
        ret = "." + dict[count] + "."
        return ret


def hash_array(bin_array):
    run_count = 0
    res_string = ""
    check = 0
    for frame in bin_array:
        # if the current frame is a 1

        """
        LOGIC ERROR:
        - RESULT BINARY ARRAY ENDING IN 1 WHEN SHOULD BE 0
        - HASH ENDS IN  'F' NOT 'G'
        - LAST 0 OF ORIGINAL BINARY ARRAY NOT BEING READ
        """
        # Bandaid fixed. Can be cleaned up/refactored/optimized

        if (frame == 1) or (check == len(bin_array) - 1):

            # Extra Checks to correctly deal with last element in the bin_array
            # Doesn't look pretty, but it functions at the very least
            if (check == len(bin_array) - 1):
                if (frame == 1):
                    char_val = countToVal(run_count)
                    res_string = res_string + char_val + '*'
                else:
                    char_val = countToVal(run_count + 1)
                    res_string = res_string + char_val
            ########################################################################
            else:
                char_val = countToVal(run_count)
                if (run_count > 0):
                    run_count = 0
                    res_string = res_string + char_val + '*'
                else:
                    res_string = res_string + char_val

        # if the current frame is a 0
        else:
            run_count = run_count + 1

        check = check + 1
    # print_test(check, "FRAME ITERATION CHECK")
    return res_string


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
            try:
                add_blank(bin_array, int(custom_flag))
            except ValueError:
                print('hashes ended with *X')
            if val != len(db_tok) - 1:
                bin_array.append(1)

        # known flag
        else:
            char_val = int(valToCount(frame_val))
            add_blank(bin_array, char_val)

            if (val != len(db_tok) - 1):
                bin_array.append(1)

    return bin_array


"""
converts frames array to binary array
"""


def frames_to_bin(frames):
    # frames to binary
    bin_array = []
    increment = 0
    for x in range(0, frames[len(frames) - 1]):
        if (frames[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
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


class rhythmAnalysis:

    def __init__(self, userTaps=None, filterResults=None):
        if (userTaps != None):
            """
            TODO: merge input_perc and input_harm into one general input
            """
            # from front end: general: [[0],[......]]
            #                 harmonic: [[1],[......]]
            #                 percussive: [[2],[......]]
            self.input_type = userTaps[0][0]
            self.user_input = userTaps[1][1:]
            # print('array dimension:', self.numOfAry)
        if (filterResults != None):
            self.filter_results = filterResults

    """
    FUNCTION TO COMPARE THE PEAKS OF THE USER INPUT TO THE DB VALUE
    """

    def onset_peak_func(self):
        # print('array dimension:', self.numOfAry)
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
        try:
            user_pattern = get_pattern(change_tempo(self.user_input, 60))
        except ZeroDivisionError as error:
            print(error)

        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song is:', db_track.id)
            peak_array = unhash_array(db_track.peak_hash_synced)
            onset_array = unhash_array(db_track.onset_hash_synced)
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
            frames to timeastamp array
            """
            peak_timestamp = librosa.frames_to_time(peak_frames, sr=22050)
            onset_timetamp = librosa.frames_to_time(onset_frames, sr=22050)
            """
            compare with the user input
            """
            match_peak, matching_rate_peak, header, tail = process_recording2(user_pattern, peak_timestamp)
            match_onset, matching_rate_onset, header, tail = process_recording2(user_pattern, onset_timetamp)
            # match_percussive, matching_rate_percussive = process_recording(self.user_input_percussive, percussive_frames)
            # match_harmonic, matching_rate_harmonic = process_recording(self.user_input_harmonic, harmonic_frames)

            matching_rate = (matching_rate_onset + matching_rate_peak) / 2
            max = 0
            print(matching_rate)
            if (match_peak or match_onset):
                if (matching_rate > .7):
                    original_timestamp = librosa.frames_to_time(bin_to_frame(unhash_array(db_track.onset_hash)),
                                                                sr=22050)
                    song_results.append({"song": db_track,
                                         "percent_match": matching_rate,
                                         "matched_pattern": onset_timetamp[header:tail],
                                         "sync_user_input": user_pattern,
                                         "start_time": original_timestamp[header]})
                    max += 1
            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results

    def onset_peak_func_harmonic(self):
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

        try:
            user_pattern_harm = change_tempo(self.user_input, 60)
        except ZeroDivisionError as error:
            print(error)

        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song id: ', db_track.id)
            harmonic_array = unhash_array(db_track.harm_hash_synced)
            harmonic_frames = bin_to_frame(harmonic_array)
            harm_timestamp = librosa.frames_to_time(harmonic_frames, sr=22050)
            match_harmonic, matching_rate_harmonic, header, tail = process_recording2(user_pattern_harm, harm_timestamp)

            max = 0

            if matching_rate_harmonic > .7:
                original_timestamp = librosa.frames_to_time(bin_to_frame(unhash_array(db_track.harm_hash)), sr=22050)
                song_results.append({"song": db_track,
                                     "percent_match": matching_rate_harmonic,
                                     "matched_pattern": harm_timestamp[header:tail],
                                     "sync_user_pattern": user_pattern_harm,
                                     "start_time": original_timestamp[header]})

                max += 1

            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results

    def onset_peak_fun_percussive(self):
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
        try:
            user_pattern_perc = change_tempo(self.user_input, 60)
        except ZeroDivisionError as error:
            print(error)

        for db_track in db_results:
            """
            convert onset_hash to binary array
            """
            print('song id: ', db_track.id)

            percussive_array = unhash_array(db_track.perc_hash_synced)
            percussive_frames = bin_to_frame(percussive_array)
            perc_timestamp = librosa.frames_to_time(percussive_frames, sr=22050)
            match_percussive, matching_rate_percussive, header,tail = process_recording2(user_pattern_perc,
                                                                                             perc_timestamp)

            # decide matching rate
            # if user only tap to harm or perc, don't let 0 matching rate effect final matching rate
            max = 0
            if match_percussive:
                if matching_rate_percussive > .7:
                    original_timestamp = librosa.frames_to_time(bin_to_frame(unhash_array(db_track.perc_hash)),
                                                                sr=22050)
                    song_results.append({"song": db_track,
                                         "percent_match": matching_rate_percussive,
                                         "matched_pattern": perc_timestamp[header:tail],
                                         "sync_user_pattern": user_pattern_perc,
                                         "start_time": original_timestamp[header]})
                    max += 1
            index += 1

        if len(song_results) < 1:
            return None
        else:
            return song_results
