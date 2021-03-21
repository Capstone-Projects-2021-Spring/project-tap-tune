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


# process music file
def process_music(filename):
    y, sr = librosa.load(filename)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times


def process_music_split(filename):
    y, sr = librosa.load(filename)
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))

    sf.write('sample_harmonic.wav', y_harm, sr)
    sf.write('sample_percussive.wav', y_harm, sr)


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

    outerLoop = (len(songSynced) - len(userSynced))
    innerLoop = len(userSynced)

    for i in range(len(songSynced) - len(userSynced)):
        for j in range(len(userSynced)):
            if songSynced[j] - error <= userSynced[j] <= songSynced[j] + error:
                numOfHit += 1

        print("# of hit : {}".format(numOfHit))
        print("mark: ", mark)
        print("Outer loop: ", outerLoop)
        print("Inner loop: ", innerLoop)
        print(numOfHit)

        match = (numOfHit * len(userSynced))/(len(songSynced))

        print("match %: ", match * 100)
        if numOfHit >= mark:
            return 1
        else:
            numOfHit = 0
    print("max # of hits : {}".format(numOfHit))
    if numOfHit >= mark:
        return 1
    else:
        return 0


# function to show graph of timiestamp as points on an horizonal line
def showBeatOnALine(timestamp, songName):
    beat_num = []
    for i in range(len(timestamp)):
        beat_num.append(0)
    fig, ax = plt.subplots()
    ax.plot(timestamp, beat_num, 'ko--')
    plt.title(songName)
    plt.show()


# function to synchronize two pattern
def synchronize(originalPattern, base):
    syncedPattern = []
    for i in originalPattern:
        syncedPattern.append(i / base)
    return syncedPattern


# print array 5 items each line
def print_long(list):
    i = j = 0
    while i < len(list):
        j += 5
        print(list[i:j])
        i = j


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


def drop_ambigious(timestamp):
    result = [timestamp[0]]
    i = 1
    while i <= len(timestamp) - 1:
        if timestamp[i] - timestamp[i - 1] >= 0.08:
            result.append(timestamp[i])
        i += 1
    return result


if __name__ == "__main__":
    # ---song file processing---
    filepath = '../../sampleMusic/birthdaySong.wav'
    songName = filepath[12:-4]
    songTimestamp = process_music_onset(filepath)
    songTimestamp = drop_ambigious(songTimestamp)
    # showBeatOnALine(songTimestamp, songName)
    songP1, songP2 = process_timestamp2(songTimestamp)
    userInput = [2.377,3.073,3.476,3.752,4.452,4.809,5.117,5.759,6.458,7.127]
    twinkleStarInput = [0.261, 0.725, 1.391, 2.046, 2.736, 3.325, 4.084, 5.197, 5.941, 6.550, 7.254, 7.957, 8.604,9.294]
    jingleBellInput = [0.830, 1.190, 1.600, 2.456, 2.878, 3.335, 4.190, 4.655, 5.088, 5.497, 5.946]
    # userP1, userP2 = process_timestamp2(userInput)
    # if compare(userP1, songP1) == 1:
    #     print("match")
    # else:
    #     print("nomatch")

    # processRecoring(twinkleStarInput)
    processRecoringPeaks(twinkleStarInput)

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
