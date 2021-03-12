# This is the code for implementation of beat matching algorithm

# 1st Analyze the music file with librosa, get timestamp array
# process array
# process input array
# comparison and matching
import math
import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import sys
import matplotlib


# process music file
def process_music(filename):
    y, sr = librosa.load(filename)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    return beat_times


# First approach of time stamp processing for pattern
#
def process_timestamp(timestamp):
    return 0


# Second approach to process song timestamp array for pattern
# 1. compute time differences between each beat
# 2. get even time difference
# 3. time difference/avg time difference as relative difference(pattern)
def process_timestamp2(timestamp):
    beat_num = [0]
    beat_diff = []
    diff = 0
    for i in range(len(timestamp) - 1):
        beat_num.append(0)
        temp = timestamp[i + 1] - timestamp[i]
        beat_diff.append(temp)
        diff += temp
    avg_diff = diff / len(timestamp)
    for i in range * len(timestamp):
        timestamp[i] = timestamp[i] / avg_diff
    return timestamp


# compare input array to song
# find out if the userPattern[a1,a2,a3...] can be found in the songPattern[s1,s2,s3...]
# a multiple C meaning the how much faster/slower userPattern is to songPattern: a1= c*s1, a2=c*s2......
# a pattern note is a match if the error after multiplying c is smaller than XX
# return 1, meaning it is a match if more than XX%(70%) of the pattern note is matched
def compare(userPattern, songPattern):
    # Decide multiple c to synchronize two pattern
    # C =
    c = 2

    error = 0.5

    # how many notes need to match to pass
    mark = math.floor(len(userPattern) * 0.7)

    # keep track of how many match appears
    numOfHit = 0

    for i in range(len(songPattern) - len(userPattern)):
        for j in range(len(userPattern)):
            if songPattern - error <= userPattern[i] * c == songPattern + error:
                numOfHit = numOfHit + 1
        if numOfHit >= mark:
            return 1
        else:
            numOfHit = 0

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

# print array 5 items each line
def print_long(list):
    i = j = 0
    while i < len(list):
        j += 5
        print(list[i:j])
        i = j


if __name__ == "__main__":
    filepath = 'sampleMusic/WeWillRockYou_short.wav'
    songName = filepath[12:-4]
    songTimestamp = process_music(filepath)
    showBeatOnALine(songTimestamp,songName)
    # patternOfSong = process_timestamp2(songTimestamp)

    # get input from front end
    # userInput =  ...
    # userInput = []
    # patternOfInput = process_timestamp2(userInput)
    
    
    # if compare(patternOfInput, patternOfSong) == 1:
    #     print("we have a match!")
    # else:
    #     print("no match found")

############################ Testing area ############################
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
