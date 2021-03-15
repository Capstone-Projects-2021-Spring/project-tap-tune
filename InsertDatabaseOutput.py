from models.analysis import AudioAnalysis
import hashingfile
import librosa



title = ""
artist = ""
release_date = ""
genre = ""


file = "" #path to file


# Loads waveform of song into y
y, sr = librosa.load(file)
onset_return = librosa.onset.onset_detect(y=y, sr=sr)
beat, tempo = librosa.beat.beat_track(y=y, sr=sr, units = 'frames')

'''
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
'''



print("the insert statement for the thing")