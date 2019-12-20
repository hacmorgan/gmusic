import sys
import spotipy
import spotipy.util as util

def show_tracks(results):
    for i, item in enumerate(results['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))

token = util.prompt_for_user_token(
        username='1288888609',
        scope='user-read-private',
        client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
        client_secret='acd6651d69ea436a86d27e0827e5b644',
        redirect_uri='http://localhost:8888/callback/')

username='1288888609'

if token:
   sp = spotipy.Spotify(auth=token)
   playlists = sp.user_playlists(username)
   for playlist in playlists['items']:
    if playlist['owner']['id'] == username:
        print()
        print(playlist['name'])
        print('  total tracks', playlist['tracks']['total'])
        results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
        tracks = results['tracks']
        show_tracks(tracks)
        while tracks['next']:
            tracks = sp.next(tracks)
            show_tracks(tracks)
else:
    print("Can't get token for", username)
