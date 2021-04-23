from models.Song import Song
import librosa
import models.analysis.AudioAnalysis as AA


def sync_hash(song_hash):
    synced_times = AA.change_tempo(
        librosa.frames_to_time(AA.bin_to_frame(AA.unhash_array(song_hash))), 60)
    synced_hash = AA.hash_array(AA.frames_to_bin(librosa.time_to_frames(synced_times)))
    return synced_hash


def update_songs_sync_hash(force_update=False):
    songs = Song.get_all()
    print("updating song sync hashes...num songs: %d" % len(songs))
    for song in songs:
        if not song.onset_hash_synced or force_update:
            synced_onset_hash = sync_hash(song.onset_hash)
            song.set_onset_hash_synced(synced_onset_hash)
        if not song.peak_hash_synced or force_update:
            synced_peak_hash = sync_hash(song.peak_hash)
            song.set_peak_hash_synced(synced_peak_hash)
        if not song.perc_hash_synced or force_update:
            synced_perc_hash = sync_hash(song.perc_hash)
            song.set_perc_hash_synced(synced_perc_hash)
        if not song.harm_hash_synced or force_update:
            synced_harm_hash = sync_hash(song.harm_hash)
            song.set_harm_hash_synced(synced_harm_hash)

    print("songs updated")
