''' Stuff for jupyter lab. not required
%matplotlib inline
import IPython.display as ipd
from ipywidgets import interact
'''

import numpy as np, scipy, matplotlib.pyplot as plt
import librosa, librosa.display
import soundfile as sf

# Loads waveform of song into x
x, sr = librosa.load('khasma.wav')

# Changes audio into harmonic/percussive wave forms
y_harmonic, y_percussive = librosa.effects.hpss(x, margin = (1.0, 10.0))

''' Not required as well to create new audio files
# Creates and saves in a file
sf.write('ex1.wav', y_harmonic,sr) #Melody Audio
sf.write('ex2.wav', y_percussive, sr) #Beat Audio

# Overwrite/load the percussive beat audio
x, sr = librosa.load('ex2.wav')
'''

# Use beat track function to save the beat timestamps or frames. Tempo is the same regardless
tempo, beat_times = librosa.beat.beat_track(y_percussive, sr=sr, units = 'time') # Time in seconds
tempo, frames = librosa.beat.beat_track(y_percussive, sr=sr, units = 'frames') # Librosa Frames

# beat_times = array<Time>, frames = array
print("\n*******************beat_times, frames***************************\n")
print(len(beat_times))
print(len(frames))

# Convert the beat tracked arrays
framesToSeconds = librosa.frames_to_time(frames, sr=sr) # Frames to Seconds array
secondsToFrames = librosa.time_to_frames(beat_times, sr=sr) # Seconds to Frames

print("\n*******************framesToSeconds, secondToFrames***************************\n")
# framesToSeconds =  array<Time>, secondsToFrames = array<Frames>
print(len(framesToSeconds))
print(len(secondsToFrames))

print("\n*******************framesToSeconds = beat_times***************************\n")
# Compare Converted Arrays with original
# print(framesToSeconds == beat_times)
# print("\n*******************secondsToFrames == frames***************************\n")
# print(secondsToFrames == frames)

# Conversion of SecondsToFrames returned some false values
# for x in range(0,len(secondsToFrames)):
#     if (secondsToFrames[x] != frames[x]):
#         print(secondsToFrames[x] - frames[x])



# Short Algorithm to create array of 0's and 1's on frame indicies
array = []
increment = 0
for x in range(0, frames[len(frames) - 1]):
    if (frames[increment] == x):
        array.append(1)
        increment += 1
    else:
        array.append(0)
print(array)