from models.Song import Song
import librosa
import AudioAnalysis as audioAnalysis
from models.Database import db, get_cursor
from models.Source import hash_array

def update_synced_hashes():
    songs = Song.get_all()

    for song in songs:
        synced_onset_hash = audioAnalysis.change_tempo(
            librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(song.onset_hash))), 60)

        synced_peak_hash = audioAnalysis.change_tempo(
            librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(song.peak_hash))), 60)

        synced_harm_hash = audioAnalysis.change_tempo(
            librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(song.harm_hash))), 60)

        synced_perc_hash = audioAnalysis.change_tempo(
            librosa.frames_to_time(audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(song.perc_hash))), 60)
        song.set_onset_hash_synced(hash=synced_onset_hash)
        song.set_peak_hash_synced(hash=synced_peak_hash)
        song.set_perc_hash_synced(hash=synced_perc_hash)
        song.set_harm_hash_synced(hash=synced_harm_hash)
    onset_hash = '.66.*I*I*Z*.36.*Z*.74.*H*I*Z*.37.*Z*.72.*I*I*.36.*Z*.36.*.36.*.55.*H*H*.37.*Z*.36.'
    onset_timestamp_from_hash = librosa.frames_to_time(
        audioAnalysis.bin_to_frame(audioAnalysis.unhash_array(onset_hash)))


# get tempo from timestamp
def get_tempo(timestamp):
    ans = len(timestamp) * 60 / timestamp[-1]
    return ans


# chenge timestamp to fit specific tempo k, ex change the song to 60 bpm, k=60
def change_tempo(timestamp, k):
    original_tempo = get_tempo(timestamp)
    rate = original_tempo / k
    adjusted = [i * rate for i in timestamp]
    return adjusted


def frames_to_bin(frames):
    bin_array = []
    increment = 0
    for x in range(0, frames[len(frames) - 1]):
        if (frames[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
    bin_array.append(1)
    return bin_array


def get_synced_hashes(filepath):
    '''timestamp>frame>bin>hash'''
    y, sr = librosa.load(filepath)

    '''onset hash'''
    '''timestamp > synced timestamp > frame > bin > hash'''
    onset_hash_synced = hash_array(frames_to_bin(librosa.time_to_frames(change_tempo(librosa.onset.onset_detect(y=y, sr=sr, units='time'), 60))))

    '''peak hash'''
    '''frame > timestamp > synced timestamp > frame > bin > hash'''
    onset_env = librosa.onset.onset_strength(y=y, sr=22050)
    peak_hash_synced = hash_array(frames_to_bin(librosa.time_to_frames(change_tempo(librosa.frames_to_time(librosa.util.peak_pick(onset_env, 3, 3, 3, 5, .5, 10)), 60))))

    '''harm hash and perc'''
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))
    '''timestamp > synced timestamp > frame > bin > hash'''
    harm_hash_synced = hash_array(frames_to_bin(librosa.time_to_frames(change_tempo(librosa.onset.onset_detect(y=y_harm, sr=sr, units='time'),60))))

    perc_hash_synced = hash_array(frames_to_bin(
        librosa.time_to_frames(change_tempo(librosa.onset.onset_detect(y=y_perc, sr=sr, units='time'), 60))))

    return onset_hash_synced,peak_hash_synced,harm_hash_synced, perc_hash_synced


#
# print('from hash:', sync)
#
#
filepath = '../../sampleMusic/birthdaySong.wav'
onset,peak,harm,perc = get_synced_hashes(filepath)
print(onset)
print(peak)
print(harm)
print(perc)

# songName = filepath[18:-4]
# y, sr = librosa.load(filepath)
# frame_onset = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
# onset_timestamp_onset_from_file = librosa.frames_to_time(frame_onset)
# print('from file:',audioAnalysis.change_tempo(onset_timestamp_onset_from_file,60))
