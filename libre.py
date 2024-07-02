import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = '6002fe2429a3402d8aa9d80b9ab42d26'
CLIENT_SECRET = '888c936f1ff74230a1e2a854e138d0c8'
REDIRECT_URI = 'http://localhost:8080/callback'

SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, 
						client_secret=CLIENT_SECRET,
						redirect_uri=REDIRECT_URI,
						scope=SCOPE)

tokenInfo = sp_oauth.get_access_token()
accessToken = tokenInfo['access_token']
sp = spotipy.Spotify(auth=accessToken)

def get_Device_Id(deviceName = "piplayer"):
	devices = sp.devices()
	for device in devices['devices']:
		if device['name'] == deviceName:
			return device['id']
	return None
	
def play_track_from_URI(trackUri, deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.start_playback(device_id = deviceId, uris=[trackUri])
		print(f"playing on {deviceName}")
	else:
		print(f"Device {deviceName} not found")
		
def play_track_by_name(track_name, deviceName = "piplayer"):
	returnedTracks = sp.search(q=track_name, type='track', limit=1)
	if returnedTracks['tracks']['items']:
		track = returnedTracks['tracks']['items'][0]
		uri = track['uri']
		name = track['name']
		mainArtist = track['artists'][0]['name']
		play_track_from_URI(uri, deviceName)
		print(f"{name} by {mainArtist}")
	else:
		print(f"No tracks found for {track_name}")

def return_current_song(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		currentSong = sp.current_playback()
		if currentSong and currentSong['is_playing']:
			track = currentSong['item']
			uri = track['uri']
			name = track['name']
			mainArtist = track['artists'][0]['name']
			print(f"{name} by {mainArtist} is currently playing")
		else:
			print("No song currently playing")
	else:
		print("No device found")

def queue_song(trackName, deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		returnedTracks = sp.search(q=trackName, type='track', limit=1)
		if returnedTracks['tracks']['items']: # find and queue song
			track = returnedTracks['tracks']['items'][0]
			uri = track['uri']
			name = track['name']
			mainArtist = track['artists'][0]['name']
			sp.add_to_queue(uri, deviceId)
			print(f"{name} by {mainArtist} added to queue")
		else:
			print(f"No tracks found for {track_name}")
	else:
		print("No device found")

def list_commands():
	try:
		with open("playerCommands.txt", "r") as file:
			commands = file.read()
			print("Available commands:\n")
			print(commands)
	except FileNotFoundError:
		print("Command file not found")

def input_handler(command):
	if command.startswith("play"):
		trackName = command.split("play",1)[1] # get song from the play command
		play_track_by_name(trackName)
	elif command.startswith("queue"):
		trackName = command.split("queue",1)[1]
		queue_song(trackName)
	elif command == "help":
		list_commands()
	elif command == "current":
		return_current_song()
	else:
		print(f"Command {command} is unknown, type 'help' to list all available commands")
		
if __name__ == "__main__":
	while True:
		command = input("Player waiting... ")
		if command == "exit":
			break
		input_handler(command)
		
