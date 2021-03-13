# This is a test file to try to sepertate a song into different layers
import librosa
import soundfile as af
import matplotlib.pyplot as plt


#
def showBeatOnALine(timestamp, songName):
    beat_num = []
    for i in range(len(timestamp)):
        beat_num.append(0)
    fig, ax = plt.subplots()
    ax.plot(timestamp, beat_num, 'ko--')
    plt.title(songName)
    plt.show()


#
def decomposemusic(filepath):

    y, sr = librosa.load(filepath)
    y_harmonic, y_percussive = librosa.effects.hpss(y, margin=(5.0, 5.0))
    # percussiveoutputpath = 'sampleOutput/' + filename + '_precussive.wav'
    # harmonicouputpath = 'sampleOutput/' + filename + '_harmonic.wav'
    # af.write(percussiveoutputpath, y_percussive, sr)
    # af.write(harmonicouputpath, y_harmonic, sr)
    return y_harmonic, y_percussive, sr


def saveOutput(filename, type, y, sr):
    path = 'sampleOutput/' + filename + '_' + type + '.wav'
    af.write(path, y, sr)


if __name__ == "__main__":
    filepath = "sampleMusic/backInBlack.wav"
    filename = filepath[12:-4]
    y_harmonic, y_percussive, sr = decomposemusic(filepath)
    timestamp_harmonic = librosa.onset.onset_detect(y=y_harmonic, sr=sr, units='time')
    print(timestamp_harmonic)
    saveOutput(filename, 'harmonic', y_harmonic, sr)
    showBeatOnALine(timestamp_harmonic, filename+'_harmonic')