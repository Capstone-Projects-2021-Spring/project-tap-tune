from models.analysis import AudioAnalysis
import hashingfile
import librosa
import ACRCloudRequest as acrcloud

# TODO: Work on Peak_Hashing, automatic imput into database

class databaseInsertSong:

    # path to Song file and ACRCloud connection saved to Object
    def __init__(self, path):
        self.file = path
        self.acrreq = acrcloud.acrCloudRequest()

    def getInsertString(self):

        # Gets ACRCloud Fingerprinted metadata back as a song object with set attributes
        song = self.acrreq.getACRSongFingerprint(self.file)
        title = song.title
        artist = song.artists
        genre = song.genres

        #Not implemented in ACRCloudRequest yet
        release_date = ""


        # Loads Song file and sets it up for hashing
        y, sr = librosa.load(self.file)
        onset_return = librosa.onset.onset_detect(y=y, sr=sr)
        # beat, tempo = librosa.beat.beat_track(y=y, sr=sr, units='frames')

        # Hashes array for onset hash
        bin_array = hashingfile.framesToBin(onset_return)
        print(bin_array)
        onset_hash = hashingfile.hash_array(bin_array)
        print(onset_hash)

        # Hashes Song file to Peak hash
        peak_hash = ""

        # Outputs SQL Line for easy input into database
        databaseinput = "INSERT INTO taptune.song VALUES \"title\" = \"" + title + "\", \"artist\" = \"" + artist + "\", \"release_date\" = " + release_date + ", \"genre\" = \"" + genre + "\", \"onset_hash\" = \"" + onset_hash + "\", \"peak_hash\" = \"" + peak_hash + "\""

        return databaseinput



#   TESTING   ###################################################################################################################
'''
string = databaseInsertSong("").getInsertString()
print(string)
'''
