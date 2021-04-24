"""
- accept user file [front end -> backend] OR accept YouTube URL

*if youtube URL we need to convert from .mp4 to .wav

- accept user input song title and song artist
- search spotify for song metadata (genre, release_date, etc.)
- present and prompt user to check information [back end-> front end]
- record user verification (yes/no) [front end -> back end]
- process song file, produce hashes
- upload song metadata and hashes into DB
- return confirmation of uploading to user [back end -> front end]
"""

import librosa, librosa.display
import spotipy
from models.Song import Song
from pytube import YouTube
from pydub import AudioSegment
import time
import numpy as np
creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
spotify = spotipy.Spotify(client_credentials_manager=creds)


def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])


def countToVal(count):
    dict = {
        0: "*",
        1: "0",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "A",
        11: "B",
        12: "C",
        13: "D",
        14: "E",
        15: "F",
        16: "G",
        17: "H",
        18: "I",
        19: "J",
        20: "K",
        21: "L",
        22: "M",
        23: "N",
        24: "O",
        25: "P",
        26: "Q",
        27: "R",
        28: "S",
        29: "T",
        30: "U",
        31: "V",
        32: "W",
        33: "X",
        34: "Y",
        35: "Z"
    }

    if count in dict.keys():
        return dict[count]

    else:
        dict.update({count : str(count)})
        ret = "."+dict[count]+"."
        return ret


def hash_array(bin_array):
    run_count = 0
    res_string = ""
    check = 0
    for frame in bin_array:
        # if the current frame is a 1

        """
        LOGIC ERROR:
        - RESULT BINARY ARRAY ENDING IN 1 WHEN SHOULD BE 0
        - HASH ENDS IN  'F' NOT 'G'
        - LAST 0 OF ORIGINAL BINARY ARRAY NOT BEING READ
        """
        # Bandaid fixed. Can be cleaned up/refactored/optimized


        if(frame == 1) or (check == len(bin_array)-1):

            # Extra Checks to correctly deal with last element in the bin_array
            # Doesn't look pretty, but it functions at the very least
            if (check == len(bin_array)-1):
                if (frame == 1):
                    char_val = countToVal(run_count)
                    res_string = res_string + char_val + '*'
                else:
                    char_val = countToVal(run_count + 1)
                    res_string = res_string + char_val
            ########################################################################
            else:
                char_val = countToVal(run_count)
                if(run_count > 0):
                    run_count = 0
                    res_string = res_string+char_val+'*'
                else:
                    res_string = res_string+char_val

        # if the current frame is a 0
        else:
            run_count = run_count + 1

        check = check+1
    # print_test(check, "FRAME ITERATION CHECK")
    return res_string


def add_blank(bin_array, count_val):
    for x in range (count_val):
        bin_array.append(0)


def binToFrames(bin_array):
    frame_array = []

    for bin_ele in range (len(bin_array)):
        if(bin_array[bin_ele] == 1):
            frame_array.append(bin_ele)

    return frame_array


def artistMod(artist):
    dict = {
        "ACDC":"AC/DC",
        "Earth Wind Fire":"Earth, Wind & Fire"
    }

    if artist in dict.keys():
        return dict[artist]

    else:
        return artist


def onset_hash(file_path):
    # Loads waveform of song into x
    x, sr = librosa.load(file_path)
    # Use beat track function to save the beat timestamps or frames. Tempo is the same regardless
    frames = librosa.onset.onset_detect(y=x, sr=sr, units='frames')  # Librosa Frames
    # frames to binary
    bin_array = []
    increment = 0
    for x in range(0, frames[len(frames) - 1]):
        if (frames[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
    bin_array.append(1)
    # converting to Hash
    test_array = binToFrames(bin_array)
    songTimestamp = librosa.frames_to_time(test_array, sr=22050)
    onset_hash = hash_array(bin_array)
    return onset_hash


def peak_hash(file_path):
    y, sr = librosa.load(file_path)
    onset_env = librosa.onset.onset_strength(y=y, sr=22050)
    peaks = librosa.util.peak_pick(onset_env, 3, 3, 3, 5, .5, 10)
    # frames to binary
    bin_array = []
    increment = 0
    for x in range(0, peaks[len(peaks) - 1]):
        if (peaks[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
    bin_array.append(1)
    # converting to Hash
    test_array = binToFrames(bin_array)
    songTimestamp = librosa.frames_to_time(test_array, sr=22050)
    peak_onset_hash = hash_array(bin_array)
    return peak_onset_hash


def harm_hash(y_harm, sr):
    frames = librosa.onset.onset_detect(y=y_harm, sr=sr, units='frames')  # Librosa Frames
    # frames to binary
    bin_array = []
    increment = 0
    for x in range(0, frames[len(frames) - 1]):
        if (frames[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
    bin_array.append(1)
    # converting to Hash
    test_array = binToFrames(bin_array)
    songTimestamp = librosa.frames_to_time(test_array, sr=22050)
    harmonic_hash = hash_array(bin_array)
    return harmonic_hash


def perc_hash(y_perc, sr):
    frames = librosa.onset.onset_detect(y=y_perc, sr=sr, units='frames')  # Librosa Frames
    # frames to binary
    bin_array = []
    increment = 0
    for x in range(0, frames[len(frames) - 1]):
        if (frames[increment] == x):
            bin_array.append(1)
            increment += 1
        else:
            bin_array.append(0)
    bin_array.append(1)
    # converting to Hash
    test_array = binToFrames(bin_array)
    songTimestamp = librosa.frames_to_time(test_array, sr=22050)
    percussive_hash = hash_array(bin_array)
    return percussive_hash


def split_hash(filepath):
    print(filepath)
    try:
        print("LIBROSA PROCESSING FOR SONG SPLITTING")
        y, sr = librosa.load(filepath)
        print("LIBROSA EFFECTS HPSS")
        y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))
        print("PROCESS HARMONIC HASH")
        harm = harm_hash(y_harm, sr)
        print("PROCESS PERRCUSSIVE HASH")
        perc = perc_hash(y_perc, sr)

        return harm, perc
    except Exception as e:
        print(e)
        return None


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

# get tempo from timestamp
def get_tempo(timestamp):
    ans = len(timestamp) * 60 / timestamp[-1]
    return ans

# chenge timestamp to fit specific tempo k, ex change the song to 60 bpm, k=60
def change_tempo(timestamp, k):
    original_tempo = get_tempo(timestamp)
    rate = original_tempo / k
    adjusted = [i * rate for i in timestamp]
    return adjusted# get tempo from timestamp


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

class Source:
    # constructor for the source class
    # @param url - youtube url if provided by the user
    # @param file - .wav file uploaded by user
    def __init__(self, url=None, file=None, title=None, artist=None, ext=None):
        self.url = url
        self.file = file
        self.title = title
        self.artist = artist
        self.ext = ext

    # function to fetch audio stream from youtube
    # returns audio stream, can be saved from call
    def fetch_youtube_audio(self):
        try:
            yt = YouTube(self.url)
            streams = yt.streams.filter(only_audio=True)

            for stream in streams:
                if stream.mime_type == "audio/mp4":
                    return stream
                    break

        except Exception as e:
            print("FAILED YOUTUBE STREAM FETCH")
            return None

    # process information provided
    # fetch audio information either url or file upload
    # run librosa analysis to obtain hash values
    # upload results to db - NOT IMPLEMENTED YET
    def process_input_url(self):
        # if the url exists
        if(self.url):
            print("PROCESSING YOUTUBE VIDEO")
            audio_stream = self.fetch_youtube_audio()
            # set the unique filename to a timestamp
            filename = str(time.time()*100.0).replace('.', '')

            # try to download the youtube audiosegment as an MP4
            try:
                """
                audio_stream.download(output_path="models/ytDownloads", filename=filename)
                filename_mp4 = "ytDownloads/" + filename + ".mp4"
                output_path = "ytConverts/" + filename + ".wav"
                time.sleep(10)
                """
                # """UNCOMMENT FOR LIVE SERVER"""
                audio_stream.download(output_path="/tmp", filename=filename)
                filename_mp4 = "/tmp/" +filename+ ".mp4"
                output_path = "/tmp/"+filename+".wav"
                print(filename_mp4)
                print("SUCCESSFULLY DOWNLOADED MP4")
            except Exception as e:
                print("FAILED DOWNLOADING MP4")

            # try to convert and download MP4 file
            try:
                convert_file = AudioSegment.from_file(file=filename_mp4, format="mp4")
                convert_file.export(out_f=output_path, format="wav")
                return output_path
            except Exception as e:
                print("FAILED TO CONVERT/SAVE as WAV")
                return 0

        else:
            return 0

        # process the file upload
        # handle any file uploads
        # return path to wav file

    def process_input_upload(self):
        if (self.file):
            filename = str(time.time() * 100.0).replace('.', '')
            output_path = "/tmp/" + filename + ".wav"
            try:
                convert_file = AudioSegment.from_file(file=self.file, format=self.ext)
                convert_file.export(out_f=output_path, format="wav")
                print("UPLOAD SUCCESSFUL CONVERSION")
                return output_path
            except Exception as e:
                print("output_path = " + output_path)
                print("ext = " + self.ext)
                print("UPLOAD FAILED TO CONVERT/SAVE as WAV")
                return 0
            pass

        else:
            pass

    # obtain metadata on song
    # create new Song object
    # return <Song> if sucessful
    # return 0 if no information was found
    def fetch_spotify_data(self):
        # create song dict to store values in
        song_dict = {
            "title": None,
            "artist": None,
            "release_date": None,
            "genre": None,
            "onset_hash": None,
            "peak_hash": None,
            "harm_hash": None,
            "perc_hash": None,
            "onset_hash_synced": None,
            "peak_hash_synced": None,
            "perc_hash_synced": None,
            "harm_hash_synced": None
        }
        if(self.artist and self.title):
            track_artists = self.artist
            track_title = self.title

            song_dict["title"] = track_title
            song_dict["artist"] = track_artists

            # Search through spotify based on the artist and title input
            results_2 = spotify.search(q=song_dict.get("title"), limit=20, type="track", market=None)
            for albums in results_2["tracks"]["items"]:
                for artist in albums["artists"]:
                    print("INPUT ARTIST = " + track_artists)
                    print("SPOTIFY ARTIST = " + artist["name"])
                    res = levenshtein_ratio_and_distance(artist["name"].lower(), track_artists.lower(), ratio_calc=True)
                    print("SIMILARITY RATIO = ", res)
                    if (res >= .6):
                        track_id = albums["id"]
                        track_release = albums["album"]["release_date"]
                        artist_id = artist["id"]
                        song_dict["release_date"] = track_release
                        song_dict["artist"] = artist["name"]
                        found = True
                        break

                    else:
                        found = False
                if (found):
                    """RETRIEVE GENRES FROM SPOTIFY ARTIST SEARCH"""
                    md_results = spotify.artist(artist_id)
                    genres = ", ".join(md_results["genres"])
                    song_dict["genre"] = genres
                    break

            if(song_dict.get("release_date") != None):
                return song_dict, 1
            else:
                print("SONG NOT FOUND IN SPOTIFY")
                for albums in results_2["tracks"]["items"]:
                    for artist in albums["artists"]:
                        print(artist["name"])
                return song_dict, 0
        else:
            print("NO ARTIST OR TITLE INPUT")
            return song_dict, 0

    # run wav file through rhythm analysis
    # @param filepath: path to the wav file to be analyzed
    # @param song: song object, populated with
    # void
    def process_wav(self, filepath, song_dict):
        print("PROCESSING WAV FILE")
        print("PROCESS ONSET HASH")
        onset = onset_hash(filepath)
        print("PROCESS PEAK HASH")
        peak = peak_hash(filepath)
        print("CONDITIONAL FOR VALID HASHES")
        if((onset != None) and (peak != None)):
            print("ADD SONGS TO SONG DICT")
            # set the onset and peak hash
            song_dict["onset_hash"] = onset
            song_dict["peak_hash"] = peak
            # obtain hrm and perc hash values
            print("PROCESS HARMONIC AND PERCUSSIVE HASHES")
            harm, perc = split_hash(filepath)
            #obtain synced hashes
            onset_hash_synced, peak_hash_synced, harm_hash_synced, perc_hash_synced = get_synced_hashes(filepath=filepath)

            song_dict["onset_hash_synced"] = onset_hash_synced
            song_dict["peak_hash_synced"] = peak_hash_synced
            song_dict["harm_hash_synced"] = harm_hash_synced
            song_dict["perc_hash_synced"] = perc_hash_synced

            # set the harm and perc hashes
            print("ADD HASHES TO SONG DICT")
            print(perc)

            song_dict["perc_hash"] = perc
            song_dict["harm_hash"] = harm

            print("=============================")
            print(song_dict)
            print("=============================")
            res = all(song_dict.values())
            if(res):
                print("INSERT SONG INTO DB")
                res_song = Song.insert(song_dict)
                print("SUCCESSFULLY INSERTED SONG")
                return res_song
            else:
                print("Song fields not filled")
                return None

        else:
            print("PEAK AND ONSET HASH NOT VALID")
            return None

    # execute functions to insert new song to db by YouTube video
    # check for url, process url for converted file, fetch metadata and crete new song in db
    # return 1 if song was processed successfully
    # return 0 if song processing failed
    def process_input(self):
        # if user uploaded file
        if(self.file):
            """
            - NEED TO CHECK THE FILE EXTENSION FOR ANY FILE CONVERSIONS
            """
            print("PROCESSING FILE")
            filepath = self.process_input_upload()
            print("TEST")
            song_dict, check = self.fetch_spotify_data()

        # if the user input is a url
        elif(self.url):
            # fetch and convert the youtube video, obtain spotify info and insert new song in db
            print("PROCESSING URL")
            filepath = self.process_input_url()
            print("PROCESS SPOTIFY DATA")
            song_dict, check = self.fetch_spotify_data()
            print(song_dict)

        #if there are no inputs
        else:
            song_dict = None
            check = False

        # check that new song exists
        if(check == 1):
            self.process_wav(filepath, song_dict)
            return filepath
        else:
            print("SPOTIFY DATA NOT FOUND SUBMISSION FAILED")
            return 0


if __name__ == "__main__":
    # sample_url = "https://www.youtube.com/watch?v=D9fAN4tEviw"
    # obj = Source(url=sample_url, artist="Greta Van Fleet", title="edge of darkness")
    #
    # check = obj.process_input()
    # if(check):
    #     print("success")
    #
    # else:
    #     print("failure")
    # #
    # # artist = "commodores"
    # # song = Song.get_by_artist(artist)
    # #
    # # print(song[0].title)

    string1 = "HER"
    string2 = "H.E.R."

    string2 = string2.replace('.', '')
    print(string2)
    res = levenshtein_ratio_and_distance(string1.lower(), string2.lower(), ratio_calc=True)
    print(res)

