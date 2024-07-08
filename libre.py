import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
import time

CLIENT_ID = '6002fe2429a3402d8aa9d80b9ab42d26'
CLIENT_SECRET = '888c936f1ff74230a1e2a854e138d0c8'
REDIRECT_URI = 'http://localhost:8080/callback'

SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing'

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, 
						client_secret=CLIENT_SECRET,
						redirect_uri=REDIRECT_URI,
						scope=SCOPE)

tokenInfo = sp_oauth.get_cached_token()
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
	returnedTracks = sp.search(q=track_name, type='track', limit=10)
	if returnedTracks['tracks']['items']:
		track = select_Track(returnedTracks['tracks']['items'])
		uri = track['uri']
		name = track['name']
		mainArtist = track['artists'][0]['name']
		play_track_from_URI(uri, deviceName)
		print(f"{name} by {mainArtist}")
	else:
		print(f"No tracks found for {track_name}")
		
def skip_current(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.next_track()
		print("Current track skipped")
		return_current_song()
	else:	
		print("No device found")

def play_previous(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.previous_track()
		sp.previous_track()
		print("Jumped back to previous song")
		return_current_song()
	else:
		print("No device found")
		
#def up_Next(deviceName = "piplayer"):
#	deviceId = get_Device_Id(deviceName)
#	if deviceId:
		

def return_current_song(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		currentSong = sp.current_playback()
		if currentSong:
			# and currentSong['is_playing']:
			track = currentSong['item']
			uri = track['uri']
			name = track['name']
			length = track['duration_ms']
			mainArtist = track['artists'][0]['name']
			currentTime = currentSong['progress_ms']
			if currentSong['is_playing']:
				print(f"{name} by {mainArtist} is currently playing: ({ms_to_minutes(currentTime)}/{ms_to_minutes(length)})")
			else:
				print(f"{name} by {mainArtist} is currently paused: ({ms_to_minutes(currentTime)}/{ms_to_minutes(length)})")
		else:
			print("No song currently playing")
	else:
		print("No device found")

def ms_to_minutes(time):
	totalSeconds = time / 1000
	minutes = int(totalSeconds // 60)
	seconds = int(totalSeconds % 60)
	if seconds < 10:
		seconds =  "0" + str (seconds)
	return f"{minutes}:{seconds}"
	

def queue_song(trackName, deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		returnedTracks = sp.search(q=trackName, type='track', limit=10)
		if returnedTracks['tracks']['items']: # find and queue song
			track = select_Track(returnedTracks['tracks']['items'])
			uri = track['uri']
			name = track['name']
			mainArtist = track['artists'][0]['name']
			sp.add_to_queue(uri, deviceId)
			print(f"{name} by {mainArtist} added to queue")
		else:
			print(f"No tracks found for {track_name}")
	else:
		print("No device found")

def select_Track(trackList):
	count = 1
	for track in trackList:
		print(f"{count}. {track['name']} by {track['artists'][0]['name']}")
		count = count + 1
	response =  input("Please enter the desired song number...")
	try:
		intValue = int (response)
		if intValue < count:
			return trackList[intValue - 1]
		else:
			print("Invalid input (too large)")
			print("Last song picked...")
			return trackList[count - 2]
	except ValueError:
		print("Invalid input (not a number)")
		print("First song picked...")
		return trackList[0]

def pause(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.pause_playback(device_id = deviceId)
		track = sp.current_playback()['item']
		name = track['name']
		print(f"{name} paused...")
	else:
		print("No device found")
		
def resume(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.start_playback(device_id = deviceId)
		track = sp.current_playback()['item']
		name = track['name']
		print(f"{name} playing...")
	else:
		print("No device found")
		
		

def list_commands():
	try:
		with open("playerCommands.txt", "r") as file:
			commands = file.read()
			print("\nAvailable commands:")
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
	elif command == "resume":
		resume()
	elif command == "pause":
		pause()
	elif command == "skip":
		skip_current()
	elif command == "previous":
		play_previous()
	else:
		print(f"Command '{command}' is unknown, type 'help' to list all available commands")
		
		
if __name__ == "__main__":
	while True:
		command = input("Player waiting... ")
		if command == "exit":
			break
		input_handler(command)
		
