import sys
import spotipy
import spotipy.util as util

scope = 'user-library-read, playlist-modify-private, user-read-recently-played, playlist-modify-public'
username='1288888609'


token = util.prompt_for_user_token(
    username='1288888609',
    scope = 'user-library-read, playlist-modify-private, user-read-recently-played, playlist-modify-public',
    client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
    client_secret='acd6651d69ea436a86d27e0827e5b644',
    redirect_uri='http://localhost:8888/callback/')

if token:
    sp = spotipy.Spotify(auth=token)
    offs=0
    results = sp.current_user_saved_tracks(limit=50, offset=0)
    print(len(results))
    print(len(results['items']))
    while(len(results['items']) == 50):
        for item in results['items']:
            track = item['track']
            print(track['name'] + ' - ' + track['artists'][0]['name'])
            s = track['uri']
            s0 = s.split(':')
            s0 = [item.strip() for item in s.split(':')]
            s0.remove('spotify')
            s0.remove('track')
            sp.user_playlist_add_tracks(username, '725vlzpFJsgCQ9fJTCAoF2', s0)
        offs += 50
        results = sp.current_user_saved_tracks(limit=50, offset=offs)
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
        identity = track['uri']
        identifier = identity.split(':')
        identifier = [item.strip() for item in identity.split(':')]
        identifier.remove('spotify')
        identifier.remove('track')
        sp.user_playlist_add_tracks(username, '725vlzpFJsgCQ9fJTCAoF2', identifier)           
else:
    print("Can't get token for", username)
