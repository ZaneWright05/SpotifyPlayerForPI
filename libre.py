import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
from time import sleep
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
refreshToken = tokenInfo['refresh_token']
expiryTime = tokenInfo['expires_at']



global autoQueue, sp, pauseEvent

pauseEvent = threading.Event()
autoQueue = False # when auto queue is gen this is true
# it will allow the whole recommended queue to be cleared by adding a new song to queue
sp = spotipy.Spotify(auth=accessToken)

def refresh_Access(): # called to refresh the token
	global accessToken, refreshToken, expiryTime, sp_oauth, sp
	
	if time.time() > expiryTime:
		tokenInfo = sp_oauth.get_cached_token()
		accessToken = tokenInfo['access_token']
		refreshToken = tokenInfo['refresh_token']
		expiryTime = tokenInfo['expires_at']
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
		#return_current_song()
	else:	
		print("No device found")

def play_previous(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		currentSong = sp.current_playback()
		if currentSong['progress_ms'] > 0:
			sp.previous_track() # must be called twice as calling once goes back to the start of current
		sp.previous_track()
		print("Jumped back to previous song")
		return_current_song()
	else:
		print("No device found")
		
def restart_track(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		sp.seek_track(0)
		print("Song restarted")
#		return_current_song()
		resume()
	else:
		print("No device found")

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
				print(f"{name} by {mainArtist} is playing: ({ms_to_minutes(currentTime)}/{ms_to_minutes(length)})")
			else:
				print(f"{name} by {mainArtist} is paused: ({ms_to_minutes(currentTime)}/{ms_to_minutes(length)})")
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
	global autoQueue
	pauseEvent.clear()
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		if autoQueue: # user choosing a song to queue clears recommended
			autoQueue = False
			clear_Queue() 
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
	sleep(0.5)
	pauseEvent.set()

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
		
def up_Next(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		queue = sp.queue()
		count = 0
		if empty_Queue() == True:
			print("Queue is empty")
		else:
			for track in queue['queue']:
				if count == 10: # next 10 playing shown
					break
				else:
					name = track['name']
					artist = track['artists'][0]['name']
					print(f"{name} by {artist}")
					count = count + 1

def seek(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		currentSong = sp.current_playback()
		flag = False # flag to play song again if the system has paused it
		if currentSong:
			if currentSong['is_playing']:
				pause()
				flag = True
			track = currentSong['item']
			length = track['duration_ms']
			position = input(f"Enter position in format mm:ss, song duration ({ms_to_minutes(length)}): ")
			try:
				minute = int (position.split(':',1)[0])
				second = abs(int (position.split(':',1)[1]))
				timeInMs = ((minute * 60) + second) * 1000
				if timeInMs >= length:
					print("Cannot seek to end of song, next track will be played instead")
					skip_current()
				elif timeInMs < 0:
					print("Cannot seek to a negative value, restarting song")
					restart_track()
				else:
					sp.seek_track(timeInMs)
				if flag == True:
					resume() 
				else: 
					sleep(0.5)
					return_current_song()
			except (IndexError, ValueError):
				print("Incorrect format or invalid input, restarting song")
				restart_track()
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

def empty_Queue(deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		queue = sp.queue()
		if len(queue['queue']) == 0:
			return True
			
		currentId = None
		previousId = None
		for track in queue['queue']:
			currentId = track['id']
			#print(f"current: {currentId}")
			#print(f"previous: {previousId}")
			if previousId is not None and  currentId != previousId: # not the same
				return False # queue not empty
			previousId = currentId
		return True
	else:
		print("No device found")
		return False

def clear_Queue(deviceName = "piplayer"): # will be used when the user add something to queue to remove recomendations
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		while empty_Queue() == False:
			sp.next_track()
			#sleep(0.05) # avoid overloading api
		print("Queue empty")
		pause()
	else:
		print("No device found")
		
def set_Vol(level, deviceName = "piplayer"):
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		try:
			level = int (level)
			if level > 100:
				sp.volume(100)
				print("Out of range, volume set to 100")
			elif level < 0:
				sp.volume(0)
				print("Out of range, volume set to 0")
			else:
				print(f"Volume set to {level}")
				sp.volume(level)
		except ValueError:
			print("A number must be entered to change volume")
	else:
		print("No device found")
		
def create_Auto_Queue(deviceName = "piplayer"):
	global autoQueue
	autoQueue = True
	deviceId = get_Device_Id(deviceName)
	if deviceId:
		artistArr = []
		genreArr = []
		trackId =[]
		currentSong = sp.current_playback()
		if currentSong:
			track = currentSong['item']
			trackId.append(track['id'])
			count = 0
			for artist in track['artists']:
				if count < 4:
					artistArr.append(artist['id'])
					count = count + 1
				for genre in (sp.artist(artistArr[0]))['genres']:
					if count < 4:
						if genre not in genreArr:
							genreArr.append(genre)	
							count = count + 1	
				recommendations = sp.recommendations(seed_track=trackId, seed_artists=artistArr, seed_genres=genreArr, limit=10)
				for track in recommendations['tracks']:
					#print(track)
					sp.add_to_queue(track['uri'], deviceId)
	else:
		print("No device found")

def track_Listener(): # look for when a song is ending/changed
	lastTrackId = None
	while True:
		pauseEvent.wait()
		currentSong = sp.current_playback()
		if currentSong:
			track = currentSong['item']
			trackId = track['id']
			if trackId != lastTrackId: # update when song changed
				return_current_song()
				print(f"Player waiting... ")
				lastTrackId = trackId
			if empty_Queue():
				create_Auto_Queue()
			#	print("nothing in queue")
		sleep(1)
			
def input_handler(command):
	refresh_Access() # will refresh access if necessary
	if command.startswith("play"):
		trackName = command.split("play",1)[1] # get song from the play command
		if trackName == "":
			print("Please enter a song to play")
		else:
			play_track_by_name(trackName)
	elif command.startswith("queue"):
		trackName = command.split("queue",1)[1]
		if trackName == "":
			print("Please enter a song to queue")
		else:
			queue_song(trackName)
	elif command.startswith("volume"):
		volume = command.split("volume",1)[1]
		if volume == "":
			print("Please enter a value to set the volume to")
		else:
			set_Vol(volume)
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
	elif command == "restart":
		restart_track()
	elif command == "upcoming":
		up_Next()
	elif command == "seek":
		seek()
	elif command == "clear":
		clear_Queue()
	else:
		print(f"Command '{command}' is unknown, type 'help' to list all available commands")
		
		
if __name__ == "__main__":
	pauseEvent.set()
	listener = threading.Thread(target=track_Listener, daemon = True)
	listener.start()
	
	while True:
		command = input("Player waiting... ").strip()
		if command == "exit":
			break
		input_handler(command)
		
