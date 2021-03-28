# This is the code for implementation of beat matching algorithm

# 1st Analyze the music file with librosa, get timestamp array
# process array
# process input array
# comparison and matching

# TODO:
#     - Another method from librosa to process music
#     - Method to decide synchronize rate C
#     - Decide acceptable error when comparing beat
#     - Better way to compare two pattern
#     - Sperate song into different layer using librosa, such as : harmonic, precaussion...

import math
import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import sys
import numpy
import matplotlib.pyplot
from flask import Flask, render_template, request, json
import soundfile as sf
import spotipy
import AudioAnalysis
import os


def get_spotify_analysis(id):
    creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef",
                                                    client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
    spotify = spotipy.Spotify(client_credentials_manager=creds)

    results_4 = spotify.audio_analysis(track_id=id)
    print("\n*****Spotify*****")
    analysis_data = []
    for res in results_4["tatums"]:
        analysis_data.append(res["start"])

    return analysis_data


# ------------------------------------------Music Processing----------------------------------------------------------
# process music file
def process_music(filename):
    y, sr = librosa.load(filename)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times


def process_music_split(filename):
    y, sr = librosa.load(filename)
    # print(y)
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))
    timestamp_harmonic = librosa.onset.onset_detect(y=y_harm, sr=sr, units='time')
    timestamp_percussive = librosa.onset.onset_detect(y=y_perc, sr=sr, units='time')
    return timestamp_harmonic, timestamp_percussive
    # sf.write('sample_harmonic.wav', y_harm, sr)
    # sf.write('sample_percussive.wav', y_harm, sr)


# process beat by finding predominant local pulse
def process_music_plp(filename):
    y, sr = librosa.load(filename)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env)
    beats_plp = np.flatnonzero(librosa.util.localmax(pulse))


# gets the peak frames of a song
def getPeaks(filename):
    y, sr = librosa.load(filename)
    onset_test = librosa.onset.onset_detect(y, sr)

    hop_length = 256
    onset_envelope = librosa.onset.onset_strength(y, sr=sr, hop_length=hop_length)

    N = len(y)
    T = N / float(sr)
    t = numpy.linspace(0, T, len(onset_envelope))

    onset_frames = librosa.util.peak_pick(onset_envelope, 7, 7, 7, 7, .5, 5)
    print(onset_frames)
    return onset_frames


# finds difference between every 2nd timestamp
def mergeBeats(timestamps):
    new_times = []
    for x in range(len(timestamps) - 2):
        dif = timestamps[x + 2] - timestamps[x]
        new_times.append(dif)

    return new_times


# detect beat by onset detection
def process_music_onset(filename):
    y, sr = librosa.load(filename)
    onset_return = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    return onset_return


# First approach of time stamp processing for pattern
def process_timestamp(timestamp):
    return 0


def drop_ambigious(timestamp):
    result = [timestamp[0]]
    i = 1
    while i <= len(timestamp) - 1:
        if timestamp[i] - timestamp[i - 1] >= 0.08:
            result.append(timestamp[i])
        i += 1
    return result


# function to synchronize two pattern
def synchronize(originalPattern, base):
    syncedPattern = []
    for i in originalPattern:
        syncedPattern.append(i / base)
    return syncedPattern


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


# process the recording in full
def processRecoring(userInput):
    # DB song prep
    filepath = '../../sampleMusic/birthdaySong.wav'
    songTimestamp = process_music_onset(filepath)
    songP1, songP2 = process_timestamp2(songTimestamp)

    # user input prep
    inputP1, inputP2 = process_timestamp2(userInput)

    # compare user input and DB info
    # ---Decision making---
    if compare(inputP1, songP1) == 1:
        print("we have a match!")
    else:
        print("no match found")


# process the recording based on peaks
def processRecoringPeaks(userInput):
    # DB song prep
    filepath = '../../sampleMusic/backInBlack.wav'
    songPeaks = getPeaks(filepath)
    output1, output2 = process_timestamp2(songPeaks)

    # User input prep
    new_input = mergeBeats(userInput)
    framestoTime = librosa.frames_to_time(output1, sr=22050)

    # ---Decision making---
    if compare(new_input, framestoTime) == 1:
        print("we have a match!")
    else:
        print("no match found")


# ----------------------------------------Hashing and Unhasing----------------------------------------------------------
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


def add_blank(bin_array, count_val):
    for x in range(count_val):
        bin_array.append(0)


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


def unhash_array(db_string):
    # print(len(db_string))
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
            add_blank(bin_array, int(custom_flag))
            if val != len(db_tok) - 1:
                bin_array.append(1)

        # known flag
        else:
            char_val = int(valToCount(frame_val))
            add_blank(bin_array, char_val)

            if (val != len(db_tok) - 1):
                bin_array.append(1)

    # print("****************SHOULD BE Length of Frames************************")
    #     # print(val)
    #     # print(len(bin_array))

    return bin_array


def binToFrames(bin_array):
    frame_array = []

    for bin_ele in range(len(bin_array)):
        if (bin_array[bin_ele] == 1):
            frame_array.append(bin_ele)

    return frame_array


# -----------------------------------------------Comparing--------------------------------------------------------------
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


# ---------------------------------------Result Showing---------------------------------------------------------------
# function to show graph of timiestamp as points on an horizonal line
def showBeatOnALine(timestamp, songName):
    beat_num = []
    for i in range(len(timestamp)):
        beat_num.append(0)
    fig, ax = plt.subplots()
    ax.plot(timestamp, beat_num, 'ko--')
    plt.title(songName)
    plt.show()


# print array 5 items each line
def print_long(list):
    i = j = 0
    while i < len(list):
        j += 5
        print(list[i:j])
        i = j


# k = original tempo / target tempo ex: for 80 tempo -> 40 tempo, k = 2
def change_tempo(timestamp, k):
    adjusted = [i * k for i in timestamp]
    return adjusted


# get user tempo
def user_tempo(user_timestamp):
    ans = len(user_timestamp) * 60 / user_timestamp[-1]
    return ans


if __name__ == "__main__":
    # ---song file processing---
    filepath = '../../sampleMusic/birthdaySong.wav'
    songName = filepath[18:-4]

    # ----------------------------tempo test-----------------------------------------------------
    """
    compare sync approach: 
    - all song are adjusted to the same standard tempo(ST), then store the adjusted timestamp hash to DB
    
    1. get user input's tempo 
    2. compare user's tempo to standard tempo
    3. adjust user timestamp to the standard tempo
    4. get user pattern using time difference between each beat
    5. iterate through the song to check if there are beats match according to the user pattern
    [2,2,4,4,6]
    
    """
    # y, sr = librosa.load(filepath)
    # onset_env = librosa.onset.onset_strength(y, sr=sr)
    # tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    # print(tempo)
    # tempo, beat = librosa.beat.beat_track(y=y, sr=sr, units='time')
    # timestamp_onset = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    # timestamp_onset = drop_ambigious(timestamp_onset)

    # ------------speed up or down tempo--------------------
    # timestamp_onset_slower = [e * 2 for e in timestamp_onset]
    # temp_cal_onset_slower = len(timestamp_onset_slower) * 60 / timestamp_onset_slower[-1] / (
    #         len(timestamp_onset_slower) / len(beat))  # <- Important
    # print(temp_cal_onset_slower)
    # print(tempo)
    #
    # print('onset timestamp len: ', len(timestamp_onset), 'tempo len: ', len(beat), 'onset_timestamp_len/beat_len: ',
    #       len(timestamp_onset) / len(beat))
    # print('onset time len: ', timestamp_onset[-1] / 60, 'beat time len: ', beat[-1] / 60)
    # # add /(len(timestamp_onset) / len(beat)) for complicated song
    # temp_cal_onset = len(timestamp_onset) * 60 / timestamp_onset[-1]  # <- Important
    # print(temp_cal_onset)
    #
    # print('tempo - temp_cal', tempo - temp_cal_onset, 'tempo/tempo_cal_onset= ', tempo / temp_cal_onset)
    # print('onset stamp', timestamp_onset)
    # print('beat stamp: ', beat)

    # tempo1 = librosa.beat.tempo(y=y, sr=sr)
    # y_2x = librosa.effects.time_stretch(y,2)
    # tempo2 = librosa.beat.tempo(y=y_2x, sr=sr)
    # print(tempo1,tempo2)

    # ---------------------------hpss AREA--------------------------------------------------------------
    # timestamp_harmonic, timestamp_percussive = process_music_split(filepath)
    # timestamp_harmonic = drop_ambigious(timestamp_harmonic)
    # timestamp_percussive = drop_ambigious(timestamp_percussive)
    # timestamp_harmonic =  drop_ambigious(timestamp_harmonic)
    # print(timestamp_harmonic)

    # showBeatOnALine(timestamp_harmonic, songName)
    # songP1, songP2 = process_timestamp2(songTimestamp)
    userInput = [2.377, 3.073, 3.476, 3.752, 4.452, 4.809, 5.117, 5.759, 6.458, 7.127]
    twinkleStarInput = [0.261, 0.725, 1.391, 2.046, 2.736, 3.325, 4.084, 5.197, 5.941, 6.550, 7.254, 7.957, 8.604,
                        9.294]
    jingleBellInput = [0.830, 1.190, 1.600, 2.456, 2.878, 3.335, 4.190, 4.655, 5.088, 5.497, 5.946]
    # userP1, userP2 = process_timestamp2(userInput)
    # if compare(userP1, songP1) == 1:
    #     print("match")
    # else:
    #     print("nomatch")

    # processRecoring(twinkleStarInput)
    # processRecoringPeaks(userInput)

# ----------------------Hash handling Area-------------------------------------------------------------------------------
# song_hash = ".66.*I*I*Z*.36.*Z*.74.*H*I*Z*.37.*Z*.72.*I*I*.36.*Z*.36.*.36.*.55.*H*H*.37.*Z*.36."
# tok = song_hash.split('*')
# print(tok)
# bin_ary = AudioAnalysis.unhash_array(song_hash)
# print(bin_ary)
# # for i in song_hash:
# #     print(i)
# y, sr = librosa.load(filepath)
# y_harm, y_perc = librosa.effects.hpss(y=y, margin = [1.0, 5.0])
# frame_harm = librosa.onset.onset_detect(y=y_harm, sr=sr)
# frame_perc = librosa.onset.onset_detect(y=y_perc, sr=sr)
# bin_array = []
# increment = 0
# for x in range(0, frame_harm[len(frame_harm) - 1]):
#     if (frame_harm[increment] == x):
#         bin_array.append(1)
#         increment += 1
#     else:
#         bin_array.append(0)
# bin_array.append(1)
# # converting to Hash
# test_array = binToFrames(bin_array)
# songTimestamp = librosa.frames_to_time(test_array, sr=22050)
# harmonic_hash = hash_array(bin_array)
# 
# bin_array = []
# increment = 0
# for x in range(0, frame_perc[len(frame_perc) - 1]):
#     if (frame_perc[increment] == x):
#         bin_array.append(1)
#         increment += 1
#     else:
#         bin_array.append(0)
# bin_array.append(1)
# # converting to Hash
# test_array = binToFrames(bin_array)
# songTimestamp = librosa.frames_to_time(test_array, sr=22050)
# perc_hash = hash_array(bin_array)
# print('harc_hash:',harmonic_hash)
# print('perc_hash:', perc_hash)
print(unhash_array(' I*.60.*0*R*S*T*R*T*R*S*P*S*E*D*A*G*E*D*E*C*S*8*5*7*5*F*B*R*F*C*R*F*D*E*B*9*B*7*C*8*B*6*D*Q*E*D*R*E*D*S*S*7*6*6*5*F*6*4*S*F*D*R*E*D*F*B*0*7*B*7*C*7*C*J*N*4*D*D*8*4*6*6*F*6*5*E*6*5*E*6*7*5*7*C*F*6*5*F*C*E*D*E*6*5*E*D*E*C*8*C*7*C*7*B*6*C*R*F*7*5*E*B*E*D*7*6*7*5*D*E*8*4*D*6*7*C*E*C*F*C*E*D*E*D*E*C*7*B*7*C*8*A*7*5*6*C*D*8*H*R*P*R*Q*Q*R*R*P*L*5*D*C*8*I*Q*P*E*C*R*Q*P*Q*E*C*Q*Q*D*B*R*Q*C*D*D*C*J*H*.40.*Q*L*6*E*C*D*C*E*D*E*6*5*E*C*9*4*6*5*8*6*B*D*D*F*D*D*5*5*0*E*C*8*5*6*4*G*4*7*8*4*7*B*6*C*M*4*E*C*F*7*3*E*7*5*E*5*5*7*5*D*8*5*8*5*C*D*E*6*6*E*D*E*C*F*5*6*E*6*5*7*6*4*8*B*7*B*7*6*6*C*C*R*Q*R*Q*8*H*R*7*6*C*R*P*L*5*C*E*Q*Q*K*5*D*C*Q*R*P*Q*D*C*Q*Q*D*B*K*6*D*B*Q*9*H*I*J*.39.*R*E*B*0*D*D*D*C*E*D*D*C*E*C*D*C*E*C*D*C*E*C*D*C*F*C*D*C*D*E*Q*C*D*P*F*C*E*C*D*D*R*D*D*E*B*E*B*L*6*E*C*E*C*D*D*J*6*8*4*D*Q*C*Y*5*E*D*M*3*R*L*5*E*C*D*C*R*D*C*E*D*D*C*F*B*R*D*E*P*R*K*6*E*C*K*6*D*D*Q*F*C*Q*C*E*Q*C*D*P*D*C*R*C*C*J*.44.*.37.*R*8*I*5*K*P*R*N*I*C*P*Q*Q*7*J*Q*J*6*D*C*B*E*Q*K*5*D*C*C*D*Q*Q*P*R*Q*D*C*8*4*C*J*I*.39.*R*.68.*5*J*D*.46.*6*C*7*9*2*I*Q*K*5*Q*7*5*D*J*5*Q*D*B*C*D*Q*P*E*5*4*C*E*Q*P*E*B*D*C*R*P*Q*D*C*Q*P*D*5*5*7*I*B*E*Q*Q*D*C*R*.52.*Q*D*D*R*D*B*B*E*R*Q*P*R*Q*Q*K*5*C*D*Q*Q*K*5*E*B*K*6*P*7*5*C*D*C*H*Y*P*R*.85.*R*N*M*8*L*5*C*B*2*I*7*9*4*D*D*4*7*E*D*J*7*E*D*D*C*Q*F*5*6*E*C*J*7*D*D*E*4*6*D*D*R*C*E*R*D*D*K*5*E*E*J*6*E*C*D*C*E*C*H*7*0*D*D*R*E*C*E*5*6*D*D*Q*S*Q*E*D*D*C*E*D*L*5*D*D*E*C*E*B*R*7*6*D*R*D*D*Q*D*D*C*6*I*E*Q*S*Q*'))

# timestamp_perc = librosa.frames_to_time(frames = frame_perc)
# print(frame_perc)
# frame_perc_diff = []
# for e in range(len(frame_perc)-1):
#     frame_perc_diff.append(frame_perc[e+1]-frame_perc[e])
# print(frame_perc_diff)
# showBeatOnALine(frame_perc,songName)


# ########################### Testing area ############################
# beat_num = [0]
# beat_diff = []
# diff = 0
# for i in range(len(beat_times)-1):
#     beat_num.append(0)
#     beat_diff.append(beat_times[i+1]-beat_times[i])
#     diff += beat_times[i+1]-beat_times[i]
# # print(beat_num)
# print_long(beat_diff)
# print('avg time diff between each beat: {}'.format((diff/len(beat_diff))))
#
#
# fig, ax = plt.subplots()
#
# ax.plot(beat_times, beat_num, 'ko--')
# plt.title('Twinkle Star')
# plt.show()
