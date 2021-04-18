import requests

CLIENT_ID = '57483e104132413189f41cd82836d8ef'
CLIENT_SECRET = '2bcd745069bd4602ae77d1a348c0f2fe'

AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token)
}

# base URL of all Spotify API endpoints
REC_ENDPOINT = '	https://api.spotify.com/v1/recommendations'

# Track ID from the URI
track_id = '2FXC3k01G6Gw61bmprjgqS'

# actual GET request with proper header
r = requests.get(REC_ENDPOINT + '/', headers=headers,
                 params={'seed_artist' : '2FXC3k01G6Gw61bmprjgqS',
                         'seed_genres' : 'rock',
                         'target_acousticness' : .1,
                         'target_danceability' : None,
                         'target_energy' : None,
                         'target_instrumentalness' : None,
                         'target_loudness' : None
                 })

d = r.json()

print(d['tracks'][0]['album']['artists'][0]['name'])
print(d['tracks'][0]['name'])