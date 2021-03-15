import numpy as np, scipy, matplotlib.pyplot as plt
import librosa, librosa.display
import soundfile as sf


def framesToBin(frames):
    # Short Algorithm to create array of 0's and 1's on frame indicies
    bin_array = []
    increment = 0
    val = int(frames[len(frames) - 1])
    print(val)

    # new implementation
    for frame_val in frames:
        print(frame_val)
        increment = 0
        while increment < frame_val:
            increment += 1
            bin_array.append(0)

        bin_array.append(1)

        return bin_array


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
        dict.update({count : str(count)})
        ret = "."+dict[count]+"."
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


        if(frame == 1) or (check == len(bin_array)-1):

            # Extra Checks to correctly deal with last element in the bin_array
            # Doesn't look pretty, but it functions at the very least
            if (check == len(bin_array)-1):
                if (frame == 1):
                    char_val = countToVal(run_count)
                    res_string = res_string + char_val + '*'
                else:
                    char_val = countToVal(run_count + 1)
                    res_string = res_string + char_val
            ########################################################################
            else:
                char_val = countToVal(run_count)
                if(run_count > 0):
                    run_count = 0
                    res_string = res_string+char_val+'*'
                else:
                    res_string = res_string+char_val

        # if the current frame is a 0
        else:
            run_count = run_count + 1

        check = check+1
    return res_string


def add_blank(bin_array, count_val):
    for x in range (count_val):
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
    print(len(db_string))
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


"""
GET THE STRING VALUE TO BE STORED IN THE DB, ONSET_FRAMES
"""
# Loads waveform of song into x
filepath = 'sampleMusic/twinkleStar.wav'
y, sr = librosa.load(filepath)
onset_return = librosa.onset.onset_detect(y=y, sr=sr)
frames = onset_return

# new implementation
bin_array = []
increment = 0
for x in range(frames[len(frames)-1]):
    if (frames[increment] == x):
        bin_array.append(1)
        increment += 1
    else:
        bin_array.append(0)

print("************RESULTS**************")
print(bin_array)

"""
res_string is the value to be stored in the database
"""
res_string = hash_array(bin_array)
print(res_string)



"""
Restore the frame array
"""
res_array = unhash_array(res_string)
print(res_array)
print(res_array == bin_array)

# frames from bin
res_frames = []
track = 0
offset = 0
check = 0

for bin in res_array:
    if(bin == 0) and (check != len(res_array)-1):
        track += 1

    elif(bin == 1):
        res_frames.append(track+offset)
        offset += 1

    else:
        res_frames.append(track + offset +1)
        offset += 1
    check += 1

print("*********************RESULT FRAMES COMPARD TO ORIGINAL FRAMES")
print(res_frames == frames)