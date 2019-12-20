import spotipy
import spotipy.util as util

token = util.prompt_for_user_token(
        username='1288888609',
        scope='user-read-private',
        client_id='b08a9cc6296b4bd89d29eb475ffc30a1',
        client_secret='acd6651d69ea436a86d27e0827e5b644',
        redirect_uri='http://localhost:8888/callback/')

spotify = spotipy.Spotify(auth=token)

results = spotify.search(q='artist: Atmosphere', type='artist')

print(results)
