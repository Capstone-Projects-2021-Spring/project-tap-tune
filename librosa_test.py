import math
import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import sys
import matplotlib


def showBeatOnALine(timestamp, songName):
    beat_num = []
    for i in range(len(timestamp)):
        beat_num.append(0)
    fig, ax = plt.subplots()
    ax.plot(timestamp, beat_num, 'ko--')
    plt.title(songName)
    plt.show()


filename = "sampleMusic/backInBlack.wav"
songName = filename[12:-4]
y, sr = librosa.load(filename)

# --------------librosa.beat.plp------------------------------
# onset_env = librosa.onset.onset_strength(y=y, sr=sr)
# pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)
#
# tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env)
# beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
# times = librosa.times_like(onset_env, sr=sr)
#
# print(times[0:100])
#
# showBeatOnALine(times, songName)

# --------------librosa.onset.onset_detect-------------------
ary = librosa.onset.onset_detect(y=y, sr=sr, units='time')
# print(ary)
showBeatOnALine(ary, songName)

syn = []
base = min(ary)
for i in ary:
    syn.append(i / base)
print(syn)

exp = {1.268, 1.690, 2.115, 2.751, 3.433, 4.081, 5.251, 5.628, 6.011, 6.706, 7.392, 8.072}
syn2 = []
base2 = min(exp)
for i in exp:
    syn2.append(i / base2)
print(syn2)
