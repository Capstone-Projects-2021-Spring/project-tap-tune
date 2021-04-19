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
import sys
import numpy
import matplotlib.pyplot
from flask import Flask, render_template, request, json
import soundfile as sf
import spotipy
import AudioAnalysis as aa
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
def get_pattern(timestamp):
    beat_diff = []
    diff = 0
    for i in range(len(timestamp) - 1):
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
    return beat_diff


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
        beat_num.append(1)
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


# chenge timestamp to fit specific tempo k, ex change the song to 60 bpm, k=60
def change_tempo(timestamp, k):
    original_tempo = get_tempo(timestamp)
    rate = original_tempo/k
    adjusted = [i * rate for i in timestamp]
    return adjusted


# get tempo from timestamp
def get_tempo(timestamp):
    ans = len(timestamp) * 60 / timestamp[-1]
    return ans


def compare_sync(song_timestamp, user_pattern):
    header = 0
    tail = 1
    error = 0.2
    hit = 0
    offset = 0
    for i in user_pattern:
        target = i + offset
        print('  find a beat ',target,' seconds away')
        while(tail<len(song_timestamp)):
            beatlength = song_timestamp[tail]-song_timestamp[header]
            if target-error<= beatlength <= target+error:
                print('    a beat found')
                hit += 1
                header = tail
                tail += 1
                offset = 0
                break;
            # if we pass the target, stimulate the target
            elif beatlength > target+error:
                print('    no beat find around target')
                offset += i
                break
            # keep moving until we find a beat or miss the target
            else:
                print('    keep moving')
                tail += 1
            print(header,tail)
    return hit


def match_temposync(song_timestamp, user_pattern):
    mark = 0.7 *  len(user_pattern)
    index_song_pattern = 0
    for i in range(len(song_timestamp)):
        print('start with ',i,' th element in song timestamp')
        numOfHit = compare_sync(song_timestamp[i:], user_pattern)
        print('number of hit for this iteration: ',numOfHit)
        if numOfHit >= mark:
            return 1, 100
    return 0,0


if __name__ == "__main__":
    # ---song file processing---
    filepath = '../../sampleMusic/TheEntertainer.wav'
    songName = filepath[18:-4]
    user_timestamp = [0.476, 0.99, 1.45, 2.148, 2.574, 3.44, 3.863, 6.302, 6.686, 7.106, 7.524, 7.872, 8.28, 8.768, 9.45, 9.798, 10.52]
    user_pattern_from_timestamp = get_pattern(change_tempo(user_timestamp, 60))
    user_pattern = [0.46, 0.508, 1.036, 0.492, 0.568, 1.094, 0.474, 0.55, 1.12, 0.458, 0.553, 1.129, 0.488, 0.564]
    print('sync pattern:',change_tempo(user_pattern,60))
    print('sync timestamp then get pattern:', user_pattern_from_timestamp)

    # ary = '.36.*D*3*2*3*5*2*3*H*8*7*7*D*I*H*H*4*6*I*2*6*3*J*5*4*8*7*.43.*N*5*3*2*3*8*4*P*7*7*9*P*2*W*4*3*2*F*5*4*5*D*B*4*8*F*4*8*2*7*A*9*A*6*A*8*9*2*6*8*0*A*6*2*6*0*C*4*2*6*9*8*0*9*3*3*3*5*0*7*4*4*J*8*2*8*7*2*6*9*4*3*9*5*4*8*0*9*7*9*2*6*4*3*A*8*9*0*9*7*8*2*7*4*3*9*A*8*0*H*B*7*8*9*9*A*A*7*B*7*4*2*A*J*9*D*4*3*6*8*9*9*8*2*9*G*I*5*4*J*0*K*5*9*8*T*0*7*9*9*0*7*8*7*2*9*B*8*7*9*E*3*C*7*8*0*7*9*9*0*8*3*3*A*9*8*0*9*9*7*9*4*3*C*7*8*0*7*9*8*2*7*0*2*3*9*9*9*0*A*6*9*4*4*4*3*A*8*9*0*6*A*9*3*4*4*4*8*4*5*9*0*K*7*G*A*9*9*4*I*4*2*2*3*8*A*9*9*0*V*D*K*9*0*A*P*8*A*4*3*C*8*A*8*8*7*E*5*8*B*7*3*5*9*8*A*I*2*J*6*4*4*8*2*2*N*0*2*7*G*2*B*3*J*9*B*7*3*5*2*6*8*9*J*.48.*8*A*9*T*9*8*J*9*0*7*I*A*8*9*9*9*B*J*7*7*A*2*6*9*B*9*6*I*D*6*B*Q*4*6*6*2*H*B*Q*4*9*E*9*B*8*8*A*7*4*3*A*8*4*7*9*5*4*K*4*8*K*U*C*3*E*E*B*9*C*3*4*4*2*6*J*B*B*9*5*8*J*9*C*G*H*D*4*P*J*4*9*9*9*9*0*J*6*I*A*9*B*6*C*6*4*9*4*4*E*9*0*J*6*A*8*9*9*4*4*2*8*I*7*4*4*C*5*A*0*9*6*2*A*A*3*K*B*G*B*7*8*A*8*A*0*8*7*3*5*9*4*3*A*L*8*H*4*4*8*A*W*E*5*4*8*5*6*6*C*6*F*6*F*E*7*6*0*.37.*7*6*4*7*4*7*J*9*B*4*J*9*0*A*G*0*G*9*J*V*7*M*5*B*9*L*5*7*5*4*0*7*C*8*9*9*6*4*3*2*K*8*9*A*B*3*4*3*C*J*8*A*G*4*3*A*I*2*8*4*5*6*9*8*A*I*9*J*4*4*8*5*4*J*A*7*9*I*4*5*0*6*9*C*6*J*8*I*2*6*.40.*C*I*6*0*T*7*3*4*T*0*L*4*J*9*9*3*5*2*U*5*8*0*H*9*0*9*6*9*E*3*W*9*3*5*9*F*A*9*9*3*6*C*9*D*A*8*C*9*9*6*9*4*3*A*8*A*0*8*M*D*A*K*T*9*6*2*7*9*8*B*7*R*K*9*2*J*G*8*D*5*B*.36.*4*4*9*9*B*H*B*8*6*K*9*0*H*E*4*8*J*4*6*.37.*8*J*9*0*.45.*A*0*7*9*.43.*3*A*8*9*D*P*7*7*B*B*I*9*9*8*A*0*6*9*2*2*3*9*9*9*7*2*Q*3*G*2*G*8*A*I*0*H*8*A*7*B*I*0*H*8*A*8*9*9*9*9*9*0*5*D*5*C*H*9*9*8*A*8*C*6*8*2*H*8*I*D*G*0*H*0*6*J*9*9*9*J*0*6*9*8*C*6*9*2*G*9*9*8*0*H*M*G*9*8*A*0*5*5*4*J*9*9*9*9*8*9*0*R*9*7*9*.71.*R*E*5*4*9*9*2*B*8*L*B*O*N*S*C*C*C*B*Z*D*3*A*M*I*9*8*2*2*6*N*2*C*I*D*J*9*3*Y*9*4*4*9*B*9*E*C*8*D*F*2*P*2*F*9*W*9*P*A*3*J*6*C*N*A*E*6*9*4*5*5*4*D*T*2*Q*I*T*4*4*C*P*A*0*9*E*.40.*C*7*8*J*J*8*2*A*5*.51.*I*L*.44.*J*9*0*T*G*9*V*G*5*D*C*G*2*.45.*9*F*4*.42.*3*A*2*G*0*G*C*B*2*D*C*N*2*B*D*W*G*9*8*3*5*A*D*0*.42.*8*9*2*7*C*8*G*9*4*2*A*J*C*I*7*8*K*8*9*9*8*2*7*4*3*9*J*A*8*9*E*3*9*A*8*0*6*M*8*3*3*4*5*8*9*A*S*4*3*C*G*0*7*0*7*9*9*4*4*8*I*2*A*6*8*J*9*0*I*9*6*4*2*9*B*K*J*6*G*.57.*N*T*5*.5414.*4*T*2*M*9*F*E*0*E*D*0*6*9*G*0*L*0*7*F*E*0*F*9*4*8*I*5*5*2*5*6*J*5*G*0*5*7*G*2*8*5*9*6*0*5*9*5*A*N*0*4*0*6*8*A*4*9*4*F*2*5*7*6*3*5*9*6*7*7*0*C*2*3*4*6*L*5*4*8*7*6*9*3*A*7*8*7*7*8*8*K*C*5*7*0*5*9*6*2*5*6*8*2*C*E*4*A*3*7*5*3*9*4*7*7*7*9*6*9*5*6*2*8*6*F*G*4*4*6*6*8*3*A*0*F*D*A*6*0*M*0*6*0*M*8*E*6*B*C*2*E*2*7*O*Q*6*3*R*8*4*2*F*D*5*9*8*2*4*A*7*A*I*2*5*9*5*7*K*7*A*R*2*E*5*B*D*F*2*U*2*F*C*F*0*E*F*7*8*0*K*A*G*F*H*J*D*5*6*I*8*U*B*E*5*7*4*4*6*7*7*.40.*H*7*D*0*5*A*F*G*0*I*3*B*S*0*D*2*H*C*6*8*H*U*E*5*A*4*H*3*8*F*Z*D*7*Q*4*P*7*7*.36.*T*6*8*5*A*G*I*H*B*5*J*5*0*F*M*8*0*4*A*5*6*3*7*7*I*C*F*H*D*5*0*S*D*6*A*5*N*2*7*6*8*7*2*4*7*3*.38.*G*6*G*5*A*G*6*8*0*Z*C*F*F*0*E*3*C*4*C*H*5*5*F*X*4*R*8*6*.36.*D*G*E*7*8*0*U*.51.*E*G*F*G*G*F*F*G*A*4*F*8*6*G*G*G*G*F*F*A*5*H*D*G*G*G*G*B*4*E*8*G*F*2*4*0*2*W*A*8*8*A*4*G*D*C*3*E*4*0*H*5*5*7*3*4*E*A*6*8*6*8*0*4*J*I*9*9*7*6*8*K*B*8*7*D*9*8*3*C*7*7*F*G*I*5*0*4*M*5*7*5*7*8*7*G*F*A*3*9*5*G*K*9*B*7*0*D*8*8*7*5*9*2*5*F*C*4*0*2*9*7*7*F*4*8*I*7*9*M*9*5*9*G*A*4*5*E*B*0*H*Y*3*A*F*L*B*8*K*A*8*0*H*3*4*A*5*B*J*8*2*4*7*7*J*K*I*7*0*8*5*5*P*9*6*0*V*0*S*H*V*6*4*7*E*I*F*5*8*H*D*0*D*G*L*B*F*F*H*5*8*4*9*0*6*8*F*J*D*F*5*9*0*4*E*B*0*E*H*V*F*F*X*G*H*I*B*3*D*I*E*0*K*6*L*G*C*6*7*H*6*N*7*8*N*5*7*N*4*L*A*F*8*7*G*J*L*7*G*M*7*7*7*K*D*H*C*0*E*0*N*6*6*2*7*D*H*G*F*M*Q*0*5*8*6*9*.65.*G*E*9*8*W*0*D*8*6*2*C*H*N*7*H*0*G*C*4*3*9*D*7*8*F*G*C*L*E*F*8*7*7*6*0*B*J*.49.*7*B*E*E*G*G*G*F*G*F*7*7*8*6*2*F*E*G*F*6*H*7*B*J*7*0*6*6*9*W*N*6*H*G*F*8*6*Q*8*V*G*5*O*G*7*6*.43.*9*C*Y*F*N*9*X*5*A*D*A*6*E*C*V*5*8*H*5*E*2*7*5*9*5*Y*W*F*H*F*O*7*H*.40.*7*H*N*5*X*2*T*0*4*A*D*4*C*X*2*6*4*O*6*F*H*O*9*.44.*B*.75.*.37.*X*.57.*.48.*I*E*C*4*Q*5*G*E*9*D*9*X*E*F*F*S*L*G*5*I*5*J*K*A*3*7*E*5*8*6*6*9*7*6*6*.44.*9*4*8*7*W*7*8*A*4*P*6*Y*4*9*6*A*D*B*5*F*K*S*G*6*9*F*F*.51.*C*7*9*J*C*7*Q*A*5*J*J*6*5*B*N*7*.65.*8*7*7*M*K*.48.*W*F*F*I*9*4*J*C*4*8*2*2*C*K*G*B*0*F*H*0*9*2*D*G*3*B*5*6*3*5*8*F*I*8*D*J*4*8*8*7*6*G*8*.51.*5*0*D*7*9*5*6*0*8*8*2*4*R*S*F*E*H*J*I*B*H*9*4*F*J*I*A*Y*V*A*4*5*4*6*D*6*0*S*D*X*.46.*G*.6'
    # ary = '.36.*D*3*2*3*5*2*3*H*8*7*.Z'
    # print(unhash_array(ary))

    #---------------------------------------------Vocal Seperation----------------------------------------------------
    # y, sr = librosa.load(filepath, duration = 60)
    # S_full, phase = librosa.magphase(librosa.stft(y))
    # S_filter = librosa.decompose.nn_filter(S_full,
    #                                        aggregate=np.median,
    #                                        metric='cosine',
    #                                        width=int(librosa.time_to_frames(2, sr=sr)))
    # S_filter = np.minimum(S_full, S_filter)
    # ----------------------------------------------tempo test-----------------------------------------------------
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
    # standard = 60
    #
    y, sr = librosa.load(filepath)
    # onset_env = librosa.onset.onset_strength(y, sr=sr)
    # tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
    # print(tempo)
    # tempo, beat = librosa.beat.beat_track(y=y, sr=sr, units='time')
    frame_onset = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
    # timestamp_onset = librosa.onset.onset_detect(y=y, sr=sr, units='time')
    # timestamp_onset_syc = change_tempo(timestamp_onset,60)
    # showBeatOnALine(timestamp_onset_syc,songName)
    result,rate, matched_pattern =aa.process_recording2(user_pattern_from_timestamp,frame_onset)
    print(rate,matched_pattern)
    # showBeatOnALine(timestamp_onset,songName)
    # print("timestamp_onset", change_tempo(timestamp_onset,1))
    # # timestamp_onset = drop_ambigious(timestamp_onset)
    #
    # song_tempo = get_tempo(timestamp_onset)
    # k = song_tempo / standard
    # timestamp_onset_re = change_tempo(timestamp_onset, k)
    # song_pattern = get_pattern(timestamp_onset_re)
    # print('timestamp_onset_re pattern', song_pattern)
    #
    # user_timestamp = [0.830, 1.190, 1.600, 2.456, 2.878, 3.335, 4.190, 4.655, 5.088, 5.497, 5.946]
    # # TODO: What if the first beat is waited too long?
    # user_tempo = get_tempo(user_timestamp)
    # k = user_tempo / standard
    # user_timestamp_re = change_tempo(user_timestamp, k)
    #
    # shift = timestamp_onset_re[0] - user_timestamp_re[0]
    # for i in range(len(user_timestamp_re)):
    #     user_timestamp_re[i] = user_timestamp_re[i] + shift
    # user_pattern = get_pattern(user_timestamp_re)
    # print('user_timestamp_re pattern', user_pattern)

    #-----------------------------printing arrays to an image--------------------------------------------
    # print('timestamp_onset_re:', timestamp_onset)
    # print('user_timestamp_re:',user_timestamp)
    # beat_num = []
    # beat_num2 = []
    # for i in range(len(timestamp_onset)):
    #     beat_num.append(1)
    #     beat_num2.append(1.1)
    # fig, ax = plt.subplots()
    # ax.plot(timestamp_onset_re, beat_num, 'ko-')
    # ax.plot(user_timestamp_re, beat_num[0:len(user_timestamp_re)], 'ro')
    # plt.title(songName)
    # plt.show()
    # ----------------------------------------------speed up or down tempo----------------------------------------------
    # timestamp_onset_slower = [e * 2 for e in timestamp_onset]
    # temp_cal_onset_slower = len(timestamp_onset_slower) * 60 / timestamp_onset_slower[-1] / (
    #         len(timestamp_onset_slower) / len(beat))  # <- Important
    # print(temp_cal_onset_slower)
    # print(tempo)
    # #
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
    # userInput = [2.377, 3.073, 3.476, 3.752, 4.452, 4.809, 5.117, 5.759, 6.458, 7.127]
    # twinkleStarInput = [0.261, 0.725, 1.391, 2.046, 2.736, 3.325, 4.084, 5.197, 5.941, 6.550, 7.254, 7.957, 8.604,
    #                     9.294]
    # jingleBellInput = [0.830, 1.190, 1.600, 2.456, 2.878, 3.335, 4.190, 4.655, 5.088, 5.497, 5.946]
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
# print(unhash_array('I*.60.*0*R*S*T*R*T*R*S*P*S*E*D*A*G*E*D*E*C*S*8*5*7*5*F*B*R*F*C*R*F*D*E*B*9*B*7*C*8*B*6*D*Q*E*D*R*E*D*S*S*7*6*6*5*F*6*4*S*F*D*R*E*D*F*B*0*7*B*7*C*7*C*J*N*4*D*D*8*4*6*6*F*6*5*E*6*5*E*6*7*5*7*C*F*6*5*F*C*E*D*E*6*5*E*D*E*C*8*C*7*C*7*B*6*C*R*F*7*5*E*B*E*D*7*6*7*5*D*E*8*4*D*6*7*C*E*C*F*C*E*D*E*D*E*C*7*B*7*C*8*A*7*5*6*C*D*8*H*R*P*R*Q*Q*R*R*P*L*5*D*C*8*I*Q*P*E*C*R*Q*P*Q*E*C*Q*Q*D*B*R*Q*C*D*D*C*J*H*.40.*Q*L*6*E*C*D*C*E*D*E*6*5*E*C*9*4*6*5*8*6*B*D*D*F*D*D*5*5*0*E*C*8*5*6*4*G*4*7*8*4*7*B*6*C*M*4*E*C*F*7*3*E*7*5*E*5*5*7*5*D*8*5*8*5*C*D*E*6*6*E*D*E*C*F*5*6*E*6*5*7*6*4*8*B*7*B*7*6*6*C*C*R*Q*R*Q*8*H*R*7*6*C*R*P*L*5*C*E*Q*Q*K*5*D*C*Q*R*P*Q*D*C*Q*Q*D*B*K*6*D*B*Q*9*H*I*J*.39.*R*E*B*0*D*D*D*C*E*D*D*C*E*C*D*C*E*C*D*C*E*C*D*C*F*C*D*C*D*E*Q*C*D*P*F*C*E*C*D*D*R*D*D*E*B*E*B*L*6*E*C*E*C*D*D*J*6*8*4*D*Q*C*Y*5*E*D*M*3*R*L*5*E*C*D*C*R*D*C*E*D*D*C*F*B*R*D*E*P*R*K*6*E*C*K*6*D*D*Q*F*C*Q*C*E*Q*C*D*P*D*C*R*C*C*J*.44.*.37.*R*8*I*5*K*P*R*N*I*C*P*Q*Q*7*J*Q*J*6*D*C*B*E*Q*K*5*D*C*C*D*Q*Q*P*R*Q*D*C*8*4*C*J*I*.39.*R*.68.*5*J*D*.46.*6*C*7*9*2*I*Q*K*5*Q*7*5*D*J*5*Q*D*B*C*D*Q*P*E*5*4*C*E*Q*P*E*B*D*C*R*P*Q*D*C*Q*P*D*5*5*7*I*B*E*Q*Q*D*C*R*.52.*Q*D*D*R*D*B*B*E*R*Q*P*R*Q*Q*K*5*C*D*Q*Q*K*5*E*B*K*6*P*7*5*C*D*C*H*Y*P*R*.85.*R*N*M*8*L*5*C*B*2*I*7*9*4*D*D*4*7*E*D*J*7*E*D*D*C*Q*F*5*6*E*C*J*7*D*D*E*4*6*D*D*R*C*E*R*D*D*K*5*E*E*J*6*E*C*D*C*E*C*H*7*0*D*D*R*E*C*E*5*6*D*D*Q*S*Q*E*D*D*C*E*D*L*5*D*D*E*C*E*B*R*7*6*D*R*D*D*Q*D*D*C*6*I*E*Q*S*Q*'))

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
