from models.Song import Song
import librosa
import AudioAnalysis as audioAnalysis

song = Song.get_by_ids(['1'])
if(song != None):
    onset_timestamp_from_hash = librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(song.onset_hash)))
    sync = audioAnalysis.change_tempo(onset_timestamp_from_hash, 60)
    print('from hash:', onset_timestamp_from_hash)
else:
    print('query failed')

filepath = '../../sampleMusic/TheEntertainer.wav'
songName = filepath[18:-4]
y, sr = librosa.load(filepath)
frame_onset = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
onset_timestamp_onset_from_file = librosa.frames_to_time(frame_onset)
print('from file:',onset_timestamp_onset_from_file)

