''' Stuff for jupyter lab. not required
%matplotlib inline
import IPython.display as ipd
from ipywidgets import interact
'''

import numpy as np, scipy, matplotlib.pyplot as plt
import librosa, librosa.display
import soundfile as sf
#
# # Loads waveform of song into x
# x, sr = librosa.load('khasma.wav')
#
# # Changes audio into harmonic/percussive wave forms
# y_harmonic, y_percussive = librosa.effects.hpss(x, margin = (1.0, 10.0))
#
# ''' Not required as well to create new audio files
# # Creates and saves in a file
# sf.write('ex1.wav', y_harmonic,sr) #Melody Audio
# sf.write('ex2.wav', y_percussive, sr) #Beat Audio
#
# # Overwrite/load the percussive beat audio
# x, sr = librosa.load('ex2.wav')
# '''
#
# # Use beat track function to save the beat timestamps or frames. Tempo is the same regardless
# tempo, frames = librosa.beat.beat_track(y_percussive, sr=sr, units = 'frames') # Librosa Frames
#
# # beat_times = array<Time>, frames = array
# print("\n*******************beat_times, frames***************************\n")
# print(len(frames))

# # Short Algorithm to create array of 0's and 1's on frame indicies
# array = []
# increment = 0
# for x in range(0, frames[len(frames) - 1]):
#     if (frames[increment] == x):
#         array.append(1)
#         increment += 1
#     else:
#         array.append(0)


def countToVal(count):
    dict = {
        0: "1",
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
        dict.update({count : str(count)})
        ret = "."+dict[count]+"."
        return ret


def hash_array(bin_array):
    run_count = 0
    res_string = ""
    for frame in array:
        # if the current frame is a 1
        if(frame == 1):
            char_val = countToVal(run_count)
            if(run_count > 0):
                run_count = 0
                res_string = res_string+char_val+"1"
            else:
                res_string = res_string+char_val

        # if the current frame is a 0
        else:
            run_count = run_count + 1

    return res_string


def add_blank(bin_array, count_val):
    for x in range (count_val):
        bin_array.append(0)


def valToCount(frame_val):
    dict = {
        0: "1",
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
    db_tok = db_string.split("1")
    print(db_tok)
    bin_array = []
    for frame_val in db_tok:
        # if custom flag
        if(frame_val == ""):
            pass

        #known flag
        else:
            char_val = int(valToCount(frame_val))
            print(char_val)
            print(type(char_val))
            add_blank(bin_array, char_val)

        bin_array.append(1)

    return bin_array


array = [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1]
res_string = hash_array(array)
print(res_string)

res_array = unhash_array(res_string)
print(res_array)
print(array)
# # Convert the beat tracked arrays
# framesToSeconds = librosa.frames_to_time(frames, sr=sr) # Frames to Seconds array
#
# print("\n*******************framesToSeconds, secondToFrames***************************\n")
# # framesToSeconds =  array<Time>, secondsToFrames = array<Frames>
# print(len(framesToSeconds))