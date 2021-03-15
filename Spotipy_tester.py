import spotipy
import json


# Set user's credencials to access Spotify data
scope = 'user-read-private user-read-playback-state user-modify-playback-state'
lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'


creds = spotipy.oauth2.SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef", client_secret="2bcd745069bd4602ae77d1a348c0f2fe")
spotify = spotipy.Spotify(client_credentials_manager=creds)

# results_4 = spotify.audio_analysis(track_id="08mG3Y1vljYA6bvDt4Wqkj")
# print("\n*****BARS*****")
# print(len(results_4["bars"]))
# print(results_4["bars"][0]["start"])
# print(results_4["bars"][1]["start"])
# print("\n*****BEATS*****")
# for res in results_4["beats"]:
#     print(res)
# print(results_4["beats"])
#
# print("\n*****Tatum*****")
# print(results_4["tatums"])

# print("\n*****SECTIONS*****")
# print(len(results_4["sections"]))
# print("\n*****SEGMENTS*****")
# print(len(results_4["segments"]))

# """GET SONG TITLES FROM ARTIST NAME w/Sample URL"""
# results_1 = spotify.search(q="Hozier", limit=10, type="track", market=None)
# for album in results_1["tracks"]["items"]:
#     print(album["name"])
#     print(album["preview_url"])

"""GET ARTIST NAMES FROM SONG TITLE w/SAMPLE URL
- take a song from the RHYTHM ANALYSIS song results
- search song (10 tracks?) get song url and artist
- compare input_artist to result_artist
- if same append song/artist/preview_URL to the song_result
"""
# results_2 = spotify.search(q="kiss kiss", limit=10, type="track", market=None)
# for albums in results_2["tracks"]["items"]:
#     preview_url = albums["preview_url"]
#     for artist in albums["artists"]:
#         print(artist["name"])
#         print(preview_url)

"""GET GENRE FROM ARTIST"""
# results_3 = spotify.search(q="Daft Punk", limit=10, type="artist", market=None)
# for artist in results_3["artists"]["items"]:
#     for genre in artist["genres"]:
#         print(genre)

"""GET ARTIST ID"""
target_artist = "Daft Punk"
artist_result = spotify.search(q=target_artist, type="artist")
genres = artist_result["artists"]["items"][0]["genres"]
target = artist_result["artists"]["items"][0]["id"]
"""GET TOP 5 TRACKS"""
tracks = spotify.artist_top_tracks(artist_id=target)

for x in range (5):
    song = tracks["tracks"][x]["name"]
    release_date = tracks["tracks"][x]["album"]["release_date"]
    print("*************")
    print(genres)
    print(target_artist)
    print(release_date)
    print(song)


