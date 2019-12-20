from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json

client_credentials_manager = SpotifyClientCredentials(
     client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
     client_secret='acd6651d69ea436a86d27e0827e5b644')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

uri = 'spotify:user:1288888609:playlist:6AbZwC9XIZkvJknheO5QYS'
username = uri.split(':')[2]
playlist_id = uri.split(':')[4]

results = sp.user_playlist(username, playlist_id)
print (json.dumps(results, indent=4))



