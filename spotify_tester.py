import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="57483e104132413189f41cd82836d8ef",
                                                           client_secret="2bcd745069bd4602ae77d1a348c0f2fe"))

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])


