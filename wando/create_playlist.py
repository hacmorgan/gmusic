import pprint
import sys
import os
import subprocess

import spotipy
import spotipy.util as util

username='1288888609'
playlist_name='Python playlist'

scope='playlist-modify-public'
token = util.prompt_for_user_token(
    username='1288888609',
    scope='playlist-modify-public',
    client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
    client_secret='acd6651d69ea436a86d27e0827e5b644',
    redirect_uri='http://localhost:8888/callback/')

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlists = sp.user_playlist_create(username, playlist_name)
                                                                           
    pprint.pprint(playlists)
else:
    print("Can't get token for", username)
