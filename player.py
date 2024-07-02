import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import logging

logging.basicConfig(level=logging.INFO)

CLIENT_ID = '6002fe2429a3402d8aa9d80b9ab42d26'
CLIENT_SECRET = '888c936f1ff74230a1e2a854e138d0c8'
REDIRECT_URI = 'http://localhost:8080/callback'

SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing'

#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
 #                                              client_secret=CLIENT_SECRET,
  #                                             redirect_uri=REDIRECT_URI,
   #                                            scope=SCOPE))

try:
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            redirect_uri=REDIRECT_URI,
                            scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    
    print(f"Navigate here: {auth_url}")
    
    response = input("Enter redicected url")
    code = sp_oauth.parse_response_code(response)
    
    if not code :
        raise Exception("failed to recieved code from URL")
        
    token_info = sp_oauth.get_access_token(code)
    print(token_info)
    sp = spotipy.Spotify(auth=token_info['access_token'])
except Exception as e:
    logging.error(f"authentification error: {e}")
    raise
    
def play_track(track_uri):
    devices = sp.devices()
    if not devices['devices']:
        print("No available devices")
        return
    
    device_id = devices['devices'][0]['id']
    sp.start_playback(device_id=device_id, uris=[track_uri])
    
    
if __name__ == "__main__":
    trackUri = 'spotify:track:77orX4NH0a9HtNXNkgbbwC'
    play_track(trackUri)
    print("Playing...")
    
    while True:
        time.sleep(10)
    
