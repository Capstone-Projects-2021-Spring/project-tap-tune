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
import time
from pytube import YouTube
from pydub import AudioSegment

creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
spotify = spotipy.Spotify(client_credentials_manager=creds)

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


# def valToCount(frame_val):
#     dict = {
#         0: "*",
#         1: "0",
#         2: "2",
#         3: "3",
#         4: "4",
#         5: "5",
#         6: "6",
#         7: "7",
#         8: "8",
#         9: "9",
#         10: "A",
#         11: "B",
#         12: "C",
#         13: "D",
#         14: "E",
#         15: "F",
#         16: "G",
#         17: "H",
#         18: "I",
#         19: "J",
#         20: "K",
#         21: "L",
#         22: "M",
#         23: "N",
#         24: "O",
#         25: "P",
#         26: "Q",
#         27: "R",
#         28: "S",
#         29: "T",
#         30: "U",
#         31: "V",
#         32: "W",
#         33: "X",
#         34: "Y",
#         35: "Z"
#     }
#
#     key_list = list(dict.keys())
#     val_list = list(dict.values())
#
#     return key_list[val_list.index(frame_val)]
#
#
# def unhash_array(db_string):
#     # print(len(db_string))
#     db_tok = db_string.split("*")
#     bin_array = []
#     char_val = ""
#     for val in range (0, len(db_tok)):
#         frame_val = db_tok[val]
#         # if blank flag
#         if(frame_val == ""):
#             if val != len(db_tok)-1:
#                 bin_array.append(1)
#
#         # if a custom flag
#         elif(frame_val[0] == "."):
#             custom_flag = frame_val[1:len(frame_val)-1]
#             add_blank(bin_array, int(custom_flag))
#             if val != len(db_tok) - 1:
#                 bin_array.append(1)
#
#         #known flag
#         else:
#             char_val = int(valToCount(frame_val))
#             add_blank(bin_array, char_val)
#
#             if(val != len(db_tok)-1):
#                 bin_array.append(1)
#
#     # print("****************SHOULD BE Length of Frames************************")
#     #     # print(val)
#     #     # print(len(bin_array))
#
#     return bin_array


def binToFrames(bin_array):
    frame_array = []

    for bin_ele in range (len(bin_array)):
        if(bin_array[bin_ele] == 1):
            frame_array.append(bin_ele)

    return frame_array


# for file in os.listdir("music"):
#     print("=================================")
#     file_parse = file.split("_")
#
#     track_artist = str(file_parse[0])
#     track_title = str(file_parse[1])[0:len(file_parse[1])-4]
#
#     file_path = "music/"+file
#
#     """SPOTIFY API TO FIND SONG ID"""
#     creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
#     spotify = spotipy.Spotify(client_credentials_manager=creds)
#     print("track_title = ", track_title)
#     results_2 = spotify.search(q=track_title, limit=10, type="track", market=None)
#     for albums in results_2["tracks"]["items"]:
#         preview_url = albums["preview_url"]
#         for artist in albums["artists"]:
#             print("spotify artist  = ", artist["name"])
#             print("track_artist = ", track_artist)
#             if(artist["name"] == track_artist):
#                 print(albums["name"])
#                 break
    """SPOTIFY API TO GET SONG METADATA"""


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
    y, sr = librosa.load(filepath)
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))

    harm = harm_hash(y_harm, sr)
    perc = perc_hash(y_perc, sr)

    return harm, perc


class Source:
    # constructor for the source class
    # @param url - youtube url if provided by the user
    # @param file - .wav file uploaded by user
    def __init__(self, url=None, file=None, title=None, artist=None):
        self.url = url
        self.file = file
        self.title = title
        self.artist = artist

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
        if(self.url):
            audio_stream = self.fetch_youtube_audio()
            """
            NEED TO SPECIFY DOWNLOAD SPACE TO TMP FOLDER
            """

            filename = str(time.time()*100.0).replace('.', '')

            audio_stream.download(output_path="ytDownloads",filename=filename)
            filename_mp4 = "ytDownloads/"+filename+".mp4"
            output_path = "ytConverts/" + filename + ".wav"

            """UNCOMMENT FOR LIVE SERVER"""
            # audio_stream.download(output_path="ytDownloads", filename=filename)
            # filename_mp4 = "/tmp/" + filename.replace('.', '') + ".mp4"
            # output_path = "/tmp/"+filename+".wav"

            convert_file = AudioSegment.from_file(file=filename_mp4, format="mp4")
            convert_file.export(out_f=output_path, format="wav")
            return output_path
        else:
            return 0


    # obtain metadata on song
    # create new Song object
    # return <Song> if sucessful
    # return 0 if no information was found
    def fetch_spotify_data(self):
        if(self.artist and self.title):
            track_artists = self.artist
            track_title = self.title

            # create song dict to store values in
            song_dict = {
                "title" : track_title,
                "artist": track_artists,
                "release_date": None,
                "genre": None,
                "onset_hash": None,
                "peak_hash": None,
                "harm_hash": None,
                "perc_hash": None
            }

            # Search through spotify based on the artist and title input
            results_2 = spotify.search(q=song_dict.get("title"), limit=10, type="track", market=None)
            for albums in results_2["tracks"]["items"]:
                for artist in albums["artists"]:
                    if (artist["name"] in track_artists):
                        track_id = albums["id"]
                        track_release = albums["album"]["release_date"]
                        artist_id = artist["id"]
                        song_dict["release_date"] = track_release
                        found = True
                        break
                if (found):
                    """RETRIEVE GENRES FROM SPOTIFY ARTIST SEARCH"""
                    md_results = spotify.artist(artist_id)
                    genres = ", ".join(md_results["genres"])
                    song_dict["genre"] = genres
                    break

            if(song_dict.get("release_date") != None):
                new_song = Song.insert(song_dict)
                print("INSERTED SONG SUCCESSFULLY")
                return new_song
            else:
                return 0
        else:
            print("NO ARTIST OR TITLE INPUT")
            return 0

    # run wav file through rhythm analysis
    # @param filepath: path to the wav file to be analyzed
    # @param song: song object, populated with
    # void
    def process_wav(self, filepath, song):
        # set the onset and peak hash
        song.set_onset_hash(onset_hash(filepath))
        song.set_peak_hash(peak_hash(filepath))
        # obtain hrm and perc hash values
        harm, perc = split_hash(filepath)
        # set the harm and perc hashes
        song.set_perc_hash(perc)
        song.set_harm_hash(harm)

    # execute functions to insert new song to db by YouTube video
    # check for url, process url for converted file, fetch metadata and crete new song in db
    # return 1 if song was processed successfully
    # return 0 if song processing failed
    def process_input(self):
        # if user uploaded file
        if(self.file):
            filepath = self.file
            res_song = self.fetch_spotify_data()

        # if the user input is a url
        elif(self.url):
            # fetch and convert the youtube video, obtain spotify info and insert new song in db
            filepath = self.process_input_url()
            res_song = self.fetch_spotify_data()

        # check that new song extists
        if(res_song):
            self.process_wav(filepath, res_song)
            return 1
        else:
            return 0


if __name__ == "__main__":
    sample_url = "https://www.youtube.com/watch?v=zwyKQnbDJRg" # Bee Gees More Than A Woman
    obj = Source(url=sample_url, artist="Bee Gees", title="More Than A Woman")

    # try:
    check = obj.process_input()
    # except Exception as e:
    #     print("FAILED CONVERSION")
