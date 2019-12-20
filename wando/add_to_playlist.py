import pprint
import sys

import spotipy
import spotipy.util as util

username='1288888609'
playlist_id='6AbZwC9XIZkvJknheO5QYS'

client_id ='b08a9cc6296b4bd89d29eb475ffc30a1'
client_secret ='acd6651d69ea436a86d27e0827e5b644'
scope = 'playlist-modify-private, user-read-recently-played, playlist-modify-public'

token = util.prompt_for_user_token(
    username='1288888609',
    scope='playlist-modify-public',
    client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
    client_secret='acd6651d69ea436a86d27e0827e5b644',
    redirect_uri='http://localhost:8888/callback/')

if token:
    sp = spotipy.Spotify(auth=token)
    song = ['2naqZkUJVRbyRqGlUFnOTA']
    results = sp.user_playlist_add_tracks(username, playlist_id, song)
    print(results)
else:
    print("Can't get token for", username)

