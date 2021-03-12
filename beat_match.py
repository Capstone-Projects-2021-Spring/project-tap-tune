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
import matplotlib
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
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0,5.0))

    sf.write('sample_harmonic.wav', y_harm, sr)
    sf.write('sample_percussive.wav', y_harm, sr)

# process beat by finding predominant local pulse
def process_music_plp(filename):
    y, sr = librosa.load(filename)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env)
    beats_plp = np.flatnonzero(librosa.util.localmax(pulse))


# detect beat by onset detection
def process_music_onset(filename):
    y, sr = librosa.load(filename)
    return librosa.onset.onset_detect(y=y, sr=sr, units='time')


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


if __name__ == "__main__":
    # Never Gonna Give You Up - 0gxyHStUsqpMadRV0Di1Qt
    # Back in Black - 08mG3Y1vljYA6bvDt4Wqkj
    # We Will Rock You - 54flyrjcdnQdco7300avMJ
    data = get_spotify_analysis("54flyrjcdnQdco7300avMJ")
    dataP1, dataP2 = process_timestamp2(data)
    print_long(dataP2)

    print("\n")
    print(len(dataP2))

    # ---song file processing---
    filepath = 'sampleMusic/twinkleStar.wav'
    songName = filepath[12:-4]
    songTimestamp = process_music_onset(filepath)
    # showBeatOnALine(songTimestamp, songName)
    songP1, songP2 = process_timestamp2(songTimestamp)

    # print("songTimeStamp")
    # print(songTimestamp)
    # print("songP1")
    # print_long(songP1)
    # print("synSongP1")
    # synSongP1 = synchronize(songP1)
    # print_long(synSongP1)
    # print("songP2")
    # print_long(songP2)
    # print("synSongP2")
    # synSongP2 = synchronize(songP2)
    # print_long(synSongP2)

    # ---input processing---
    # get input from front end
    # userInput =  ...
    # userInput = [1.268, 1.690, 2.115, 2.751, 3.433, 4.081, 5.251, 5.628, 6.011, 6.706, 7.392, 8.072]
    userInput = [1.923,2.517,3.108,3.728,4.337,4.931,5.554,6.770,7.397,7.970,8.631,9.273,9.884, 10.541,11.286]
    inputP1, inputP2 = process_timestamp2(userInput)
    print("inputP1")
    print(inputP1)
    # print("synInputP1")
    # synInputP1 = synchronize(inputP1)
    # print_long(synInputP1)
    # showBeatOnALine(userInput, "user jinglebell")

    # ---Decision making---
    if compare(inputP1, songP1) == 1:
        print("we have a match!")
    else:
        print("no match found")

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
