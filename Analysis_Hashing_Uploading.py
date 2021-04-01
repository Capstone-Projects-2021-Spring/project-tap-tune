import numpy as np, scipy, matplotlib.pyplot as plt
import librosa, librosa.display
import soundfile as sf
import os
import spotipy
# from database_sep import db, get_cursor
from models.Song import Song


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


def valToCount(frame_val):
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

    key_list = list(dict.keys())
    val_list = list(dict.values())

    return key_list[val_list.index(frame_val)]


def unhash_array(db_string):
    # print(len(db_string))
    db_tok = db_string.split("*")
    bin_array = []
    char_val = ""
    for val in range (0, len(db_tok)):
        frame_val = db_tok[val]
        # if blank flag
        if(frame_val == ""):
            if val != len(db_tok)-1:
                bin_array.append(1)

        # if a custom flag
        elif(frame_val[0] == "."):
            custom_flag = frame_val[1:len(frame_val)-1]
            add_blank(bin_array, int(custom_flag))
            if val != len(db_tok) - 1:
                bin_array.append(1)

        #known flag
        else:
            char_val = int(valToCount(frame_val))
            add_blank(bin_array, char_val)

            if(val != len(db_tok)-1):
                bin_array.append(1)

    # print("****************SHOULD BE Length of Frames************************")
    #     # print(val)
    #     # print(len(bin_array))

    return bin_array


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


def printSongs(songs):
    for song in songs:
        print("++++++++++++++++++++++++++++++++")
        print(song.title)
        print(song.artist)
        print(song.release_date)
        print(song.genre)
        print("HASHES:")
        print(song.onset_hash)
        print(song.peak_hash)
        print(song.harm_hash)
        print(song.perc_hash)


def onset_hash(file_path, songs):
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
    songs[element].onset_hash = onset_hash


def peak_hash(file_path, songs):
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
    songs[element].peak_hash = peak_onset_hash


def harm_hash(y_harm, sr, songs):
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
    songs[element].harm_hash = harmonic_hash


def perc_hash(y_perc, sr, songs):
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
    songs[element].perc_hash = percussive_hash


creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
spotify = spotipy.Spotify(client_credentials_manager=creds)

songs = []
"""GATHERING INFORMATION ON SONG FILES
- SPOTIFY TESTER TO GET METADATA
- RUN LIBROSA AND HASHING ON FILES 
- SAVE INFORMATION IN SONGS LIST
"""
element = 0
for filename in os.listdir("music"):
    # parse scheme for splitting title and artist (separated by an underscore)
    filename_split = filename.split("_")
    track_id = ""
    artist_id = ""
    track_artist = str(filename_split[0])

    # parse scheme for multiple artists (separated by a comma)
    track_artists = track_artist.split(",")
    # mod any artists names
    for ele in range(len(track_artists)):
        track_artists[ele] = artistMod(track_artists[ele])

    track_title = str(filename_split[1])[0:len(filename_split[1])-4]
    song = Song(song_id=None, title=track_title, artist=", ".join(track_artists), release_date=None, genre=None, onset_hash=None,
                peak_hash=None, perc_hash=None, harm_hash=None)
    songs.append(song)
    """SEARCH THROUGH SPOTIFY AND CHECK ARTISTS"""
    found = False
    results_2 = spotify.search(q=track_title, limit=10, type="track", market=None)
    for albums in results_2["tracks"]["items"]:
        for artist in albums["artists"]:
            if(artist["name"] in track_artists):
                track_id = albums["id"]
                track_release = albums["album"]["release_date"]
                artist_id = artist["id"]
                songs[element].release_date = track_release
                found = True
                break
        if(found):
            """RETRIEVE GENRES FROM SPOTIFY ARTIST SEARCH"""
            md_results = spotify.artist(artist_id)
            genres = ", ".join(md_results["genres"])
            songs[element].genre = genres
            break

    """PERFORM ONSET HASHING"""
    file_path = "music/" + filename
    onset_hash(file_path=file_path, songs=songs)

    """PERFORM PEAK ONSET HASHING"""
    peak_hash(file_path=file_path, songs=songs)

    """SPLITTING SONG INTO HARMONICS AND PERCUSSIVE"""
    y, sr = librosa.load(file_path)
    y_harm, y_perc = librosa.effects.hpss(y, margin=(1.0, 5.0))

    """PERFORM HARMONIC HASHING"""
    harm_hash(y_harm=y_harm, sr=sr, songs=songs)

    """PERFORM PERCUSSIVE HASHING"""
    perc_hash(y_perc=y_perc, sr=sr, songs=songs)

    element += 1

"""CHECKPOINT BEFORE INSERTING INTO DB"""
printSongs(songs)
choice = input("\nVerified Information and Ready to Insert into Database? (y/n)")

if(choice == "y"):
    """INSERT INTO DATABASE
    - SEARCH TO MAKE SURE THERE ARE NO DUPLICATES
    - INSERT INFORMATION INTO THE DATABASE
    """
    try:
        cursor = get_cursor()

        # iterate through the songs
        for track in songs:
            isDup = False
            # statement to search for matching song titles
            dup_sql= 'SELECT artist FROM song WHERE title LIKE "%{0}%"'.format(track.title)
            cursor.execute(dup_sql)
            results = cursor.fetchall()
            # converting track artist string to list
            track_artists = track.artist.split(", ")
            # loops through resulting rows
            for res_record in results:
                # loops thorugh the
                for res_artist in res_record[0].split(", "):

                    if(res_artist in track_artists):
                        isDup = True
                        break

            if(isDup):
                print("DUPLICATE FOUND")

            else:
                print("NO DUPLICATE FOUND")

                """INSERT THE NEW RECORD INTO DATABASE"""
                insert_sql = "INSERT INTO song (title, artist, release_date, genre, onset_hash, peak_hash) VALUES (%s, %s, %s, %s, %s, %s)"
                vals = (track.title, track.artist, track.release_date, track.genre, track.onset_hash,
                        track.peak_hash)
                cursor.execute(insert_sql, vals)
                db.commit()

                cursor.execute('SELECT id FROM song WHERE artist = %s and title = %s', (track.artist, track.title))
                track.id = cursor.fetchall()[0][0]

                insert_sql = "INSERT INTO fingerprint (song_id, perc_hash, harm_hash) VALUES(%s, %s, %s)"
                vals = (track.id, track.perc_hash, track.harm_hash)
                cursor.execute(insert_sql, vals)
                db.commit()

    except Exception as e:
        print(e)

else:
    print("NOPE")
