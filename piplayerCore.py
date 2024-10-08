import spotipy
from spotipy.oauth2 import SpotifyOAuth
import threading
from time import sleep
import time

class piplayerCore:

	def __init__(self):
		# initialise player info
		self.CLIENT_ID = '6002fe2429a3402d8aa9d80b9ab42d26'
		self.CLIENT_SECRET = '888c936f1ff74230a1e2a854e138d0c8'
		self.REDIRECT_URI = 'http://localhost:8080/callback'
		self.SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing,user-read-recently-played'
	
		# initialise tokens for the player authorisation and refreshing
		self.sp_oauth = SpotifyOAuth(client_id=self.CLIENT_ID, 
						client_secret=self.CLIENT_SECRET,

						redirect_uri=self.REDIRECT_URI,
						scope=self.SCOPE)
# 		# Get the authorization URL
# 		auth_url = self.sp_oauth.get_authorize_url()
# 		print(f"Please navigate to this URL to authorize the application: {auth_url}")

# # Manually paste the redirect URL with the token you get after authorizing
# 		response = input("Paste the URL you were redirected to here: ")

# Extract the access token
		#tokenInfo = self.sp_oauth.get_access_token(response)

		# try:
		# 	tokenInfo = self.sp_oauth.get_access_token(response)
		# 	self.access_token = tokenInfo['access_token']
		# 	print("Access token obtained successfully.")
		# except spotipy.oauth2.SpotifyOauthError as e:
		# 	print(f"An error occurred: {e}")

# Create a Spotipy client
		

		# #tokenInfo = self.sp_oauth.get_cached_token()
		# if not tokenInfo:
		# #	tokenInfo = self.sp_oauth.get_access_token()
		# 	#self.accessToken = tokenInfo['access_token']
		# 	self.refreshToken = tokenInfo['refresh_token']
		# 	self.expiryTime = tokenInfo['expires_at']	
		
		# # variable for access to spotipy functions
		# self.sp = spotipy.Spotify(auth=self.accessToken)

		tokenInfo = self.sp_oauth.get_cached_token()
		# if not tokenInfo:
		# 	tokenInfo = self.sp_oauth.get_access_token()
		# self.accessToken = tokenInfo['access_token']
		# self.refreshToken = tokenInfo['refresh_token']
		# self.expiryTime = tokenInfo['expires_at']	



		if tokenInfo:
			if self.sp_oauth.is_token_expired(tokenInfo):
				print("Token expired, refreshing token...")
				tokenInfo = self.sp_oauth.refresh_access_token(tokenInfo['refresh_token'])
		else:
    		# No cached token, request new authorization
			print("No cached token found, please authorize.")
			auth_url = self.sp_oauth.get_authorize_url()
			print(f"Please navigate to this URL to authorize: {auth_url}")
			
			# Manually input the URL you are redirected to after authorization
			response_url = input("Paste the URL you were redirected to here: ")
			
			# Get the authorization code from the URL
			code = self.sp_oauth.parse_response_code(response_url)
			
			# Get new access token
			tokenInfo = self.sp_oauth.get_access_token(code)
		
		self.accessToken = tokenInfo['access_token']

		# variable for access to spotipy functions

		self.accessToken = tokenInfo['access_token']

		self.sp = spotipy.Spotify(auth=self.accessToken)
		
		self.autoQueue = False # FLAG for loading auto queue funtionality
		
		# initialise threading and pause event
		# ~ self.pauseEvent = threading.Event()
		# ~ self.pauseEvent.set()
		
		# ~ self.listener = threading.Thread(target=self.track_Listener, daemon=True)
		# ~ self.listener.start()
	
	def get_device_id(self, deviceName="piplayer"):
		devices = self.sp.devices()
		for device in devices['devices']:
			if device['name'] == deviceName:
				return device['id']
		return None
		
	# not like us uri for testing: spotify:track:6AI3ezQ4o3HUoP6Dhudph3
	def play_track_from_URI(self, trackUri, deviceName="piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			self.sp.start_playback(device_id = deviceId, uris=[trackUri])
			print(f"playing on {deviceName}")
		else:
			print(f"Device {deviceName} not found")
	
	def resume(self, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			self.sp.start_playback(device_id = deviceId)
			track = self.sp.current_playback()['item']
			name = track['name']
			print(f"{name} playing...")
		else:
			print("No device found")
		
	def pause(self, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			self.sp.pause_playback(device_id = deviceId)
			track = self.sp.current_playback()['item']
			name = track['name']
			print(f"{name} paused...")
		else:
			print("No device found")
			
	def set_Vol(self, level, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			level = int (float(level))
			self.sp.volume(level)
			print(f"Volume set to {level}")
		else:
			print("No device found")
	
	def seek(self, position, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			self.sp.seek_track(position)
		else:
			print("No device found")

	def play_previous(self, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			currentSong = self.sp.current_playback()
			if currentSong['progress_ms'] > 1000:
				self.sp.previous_track() # must be called twice as calling once goes back to the start of current
			self.sp.previous_track()
			print("Returned to previous song")
		else:
			print("No device found")
			
	def play_next(self, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			self.sp.next_track()
			print("Current track skipped")
		else:	
			print("No device found")
	
	def search(self, query, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			results = self.sp.search(q=query, limit = 20, type = 'track')['tracks']['items']
			return results
		else:	
			print("No device found")
			
	def refresh_access(self): # called to refresh the token
		if time.time() > self.expiryTime - 60:
			print("attempting refresh")
			tokenInfo = self.sp_oauth.get_access_token(self.refreshToken, as_dict=False)
			self.accessToken = tokenInfo['access_token']
			self.refreshToken = tokenInfo['refresh_token']
			self.expiryTime = tokenInfo['expires_at']
			self.sp = spotipy.Spotify(auth=self.accessToken)
			print("access refreshed")
	
	def get_current_song(self, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			return self.sp.current_playback()['item']
	
	def queue_from_uri(self, trackUri, deviceName = "piplayer"):
		deviceId = self.get_device_id(deviceName)
		if deviceId:
				self.sp.add_to_queue(trackUri, deviceId)
		else:
			print("No device found")
	
	def get_current_state(self, deviceName = "piplayer"):
		# self.refresh_access()
		deviceId = self.get_device_id(deviceName)
		if deviceId:
			currentSong = self.sp.current_playback()
			if currentSong:
				track = currentSong['item']
				uri = track['uri']
				name = track['name']
				length = track['duration_ms']
				mainArtist = track['artists'][0]['name']
				currentTime = currentSong['progress_ms']
				volume = currentSong['device']['volume_percent']
				imgURL = track['album']['images'][0]['url'] if track['album']['images'] else "" 
				queue = self.sp.queue()
				if queue and queue.get('queue'):
					nextSong = queue['queue'][0]
					nextURL = nextSong['album']['images'][0]['url'] if nextSong.get('album') and nextSong['album'].get('images') else None
					allQueue = queue['queue']
				
				
				# ~ # get previous song
				# ~ justPlayed = self.sp.current_user_recently_played(limit=20)
				# ~ prevName = None
				# ~ prevURL = None
				# ~ if justPlayed and justPlayed['items']:
					# ~ recent = justPlayed['items']
					# ~ for i in range(1, len(recent)):
						# ~ if recent[i]['track']['uri'] == uri:
							# ~ if i > 0:
								# ~ pSong = justPlayed['items'][i-1]['track']
								# ~ prevName = pSong['name']
								# ~ prevURL = pSong['album']['images'][0]['url'] if pSong['album']['images'] else None
								# ~ print(prevURL)
								# ~ break
				return {
					'playing' : currentSong['is_playing'],
					'currURI' : uri,
					'name' : name,
					'length' : length,
					'currentTime' : currentTime,
					'volume' : int(volume),
					'imgURL' : imgURL,
					'nextURL': nextURL,
					'queue' : allQueue,
					'playType' : currentSong['context']
					# ~ 'prevName' : prevName,
					# ~ 'prevURL' : prevURL
				}
		else:
			print("No device found")
			return None
