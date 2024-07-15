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
		self.SCOPE = 'user-read-playback-state,user-modify-playback-state,user-read-currently-playing'
	
		# initialise tokens for the player authorisation and refreshing
		self.sp_oauth = SpotifyOAuth(client_id=self.CLIENT_ID, 
						client_secret=self.CLIENT_SECRET,
						redirect_uri=self.REDIRECT_URI,
						scope=self.SCOPE)
		
		tokenInfo = self.sp_oauth.get_cached_token()
		self.accessToken = tokenInfo['access_token']
		self.refreshToken = tokenInfo['refresh_token']
		self.expiryTime = tokenInfo['expires_at']	
		
		# variable for access to spotipy functions
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
	def play_track_from_URI(self, trackUri ="spotify:track:6AI3ezQ4o3HUoP6Dhudph3" , deviceName="piplayer"):
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
