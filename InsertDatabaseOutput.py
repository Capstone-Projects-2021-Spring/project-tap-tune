from models.analysis import AudioAnalysis
import hashingfile
import librosa
import ACRCloudRequest as acrcloud

class databaseInsertSong:
    def __init__(self, path):
        self.file = path
        self.acrreq = acrcloud.acrCloudRequest()

    def getInsertString(self):

        song = self.acrreq.getACRSongFingerprint(self.file)
        title = song.title
        artist = song.artists
        genre = song.genres

        #Not implemented in ACRCloudRequest
        release_date = ""


        y, sr = librosa.load(self.file)
        onset_return = librosa.onset.onset_detect(y=y, sr=sr)
        # beat, tempo = librosa.beat.beat_track(y=y, sr=sr, units='frames')

        bin_array = hashingfile.framesToBin(onset_return)
        print(bin_array)
        onset_hash = hashingfile.hash_array(bin_array)
        print(onset_hash)
        peak_hash = ""


        databaseinput = "INSERT INTO taptune.song VALUES \"title\" = \"" + title + "\", \"artist\" = \"" + artist + "\", \"release_date\" = " + release_date + ", \"genre\" = \"" + genre + "\", \"onset_hash\" = \"" + onset_hash + "\", \"peak_hash\" = \"" + peak_hash + "\""

        return databaseinput




string = databaseInsertSong("C:\\Users\\2015d\OneDrive\Desktop\.wav files\DaftPuck_OneMoreTime.wav").getInsertString()
print(string)



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