# This is a test file to try to sepertate a song into different layers
import librosa
import soundfile as af
import matplotlib.pyplot as plt
from analysis import beat_match


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


def drop_ambigious(timestamp):
    result = [timestamp[0]]
    i = 1
    while i <= len(timestamp) - 1:
        if timestamp[i] - timestamp[i - 1] >= 0.08:
            result.append(timestamp[i])
        i += 1
    return result


def compare(userPattern, timestamp_song):
    numOfHit = 0
    mark = len(userPattern) * 0.7
    for i in range(len(timestamp)):
        numOfHit = 0
        for j in range(len(userPattern)):
            nextBeatToFind = timestamp[i] + userPattern[j]
            if findNextBeat(timestamp[i:], nextBeatToFind) == 1:
                numOfHit += 1
        print(numOfHit)
        if numOfHit >= mark:
            print("match")
            break


def findNextBeat(timestamp, beatToFind):
    i = 0
    while timestamp[i] <= beatToFind + 0.1:
        if beatToFind - 0.1 <= timestamp[i] <= beatToFind + 0.1:
            print("timestamp[i]: {} beatToFInd: {}".format(timestamp[i], beatToFind))
            return 1
        i += 1


if __name__ == "__main__":
    filepath = "sampleMusic/backInBlack.wav"
    filename = filepath[12:-4]
    userInput = [2.377,3.073,3.476,3.752,4.452,4.809,5.117,5.759,6.458,7.127]
    userP1, userP2 = beat_match.process_timestamp2(userInput)
    timestamp = beat_match.process_music_onset(filepath)
    print(timestamp)
    timestamp = drop_ambigious(timestamp)
    beat_match.print_long(timestamp)
    compare(userP1, timestamp)
    showBeatOnALine(timestamp, filename)
    # y_harmonic, y_percussive, sr = decomposemusic(filepath)
    # timestamp_harmonic = librosa.onset.onset_detect(y=y_harmonic, sr=sr, units='time')
    # print(timestamp_harmonic)
    # saveOutput(filename, 'harmonic', y_harmonic, sr)
    # showBeatOnALine(timestamp_harmonic, filename+'_harmonic')
