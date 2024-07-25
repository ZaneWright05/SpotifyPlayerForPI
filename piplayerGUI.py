from tkinter import *
from tkinter import ttk
from piplayerCore import piplayerCore
from PIL import Image, ImageTk, ImageFilter
import os
import json
import requests
from io import BytesIO

class piplayerGUI:
	def __init__(self,root):
		self.root = root
		self.root.title("piplayer")
		self.player = piplayerCore()
		
		scriptDir = os.path.dirname(__file__)
		
		playPath = os.path.join(scriptDir, 'resources', 'play.png')
		self.playImage = Image.open(playPath).resize((50, 50), Image.Resampling.LANCZOS)
		self.playPhoto = ImageTk.PhotoImage(self.playImage)
		
		pausePath = os.path.join(scriptDir, 'resources', 'pause.png')
		self.pauseImage = Image.open(pausePath).resize((50, 50), Image.Resampling.LANCZOS)
		self.pausePhoto = ImageTk.PhotoImage(self.pauseImage)
		
		stopPath = os.path.join(scriptDir, 'resources', 'stop.png')
		self.stopImage = Image.open(stopPath).resize((50, 50), Image.Resampling.LANCZOS)
		self.stopPhoto = ImageTk.PhotoImage(self.stopImage)
		
		previousPath = os.path.join(scriptDir, 'resources', 'previous.png')
		self.previousImage = Image.open(previousPath).resize((50, 50), Image.Resampling.LANCZOS)
		self.previousPhoto = ImageTk.PhotoImage(self.previousImage)
		
		nextPath = os.path.join(scriptDir, 'resources', 'next.png')
		self.nextImage = Image.open(nextPath).resize((50, 50), Image.Resampling.LANCZOS)
		self.nextPhoto = ImageTk.PhotoImage(self.nextImage)
		
		defaultPath = os.path.join(scriptDir, 'resources', 'defaultThumbnail.png')
		self.defaultImage = Image.open(defaultPath).resize((150, 150), Image.Resampling.LANCZOS)
		self.defaultPhoto = ImageTk.PhotoImage(self.defaultImage)
		
		self.defaultImageSmall = Image.open(defaultPath).resize((100, 100), Image.Resampling.LANCZOS)
		self.defaultPhotoSmall = ImageTk.PhotoImage(self.defaultImageSmall)
		
		self.imageDir = os.path.join(scriptDir, 'imageDir') # path to directory that stores the images
		if not os.path.exists(self.imageDir):
			os.makedirs(self.imageDir)
		
		# ~ self.urlMapPath = os.path.join(self.imageDir, 'url_map.json')
		# ~ if os.path.exists(self.urlMapPath):
			# ~ with open(self.urlMapPath, 'r') as f:
				# ~ self.urlMap = json.load(f)
		# ~ else:
			# ~ self.urlMap = {}
					
		self.create_buttons()
		self.updateInterval = 500
		self.volChange = BooleanVar(value=False)
		
		self.reply = None # used to store song info - reduce calls
		# ~ self.previousImg = 	None
		
		
		self.currentImgURL = None # used
		# ~ self.currentImg = None
		
		self.nextImgURL = None
		# ~ self.nextImg = None
		
		self.request_status()
	
	
	# used for faster img loading - will be properly used later
	# https://i.scdn.co/image/ab67616d0000b273cdb645498cd3d8a2db4d05e1
	# url format - needs to be converted to name for load to work 
	
	def load_image(self, url): # load image from online or locally
		localName = self.gen_local_name(url)
		localPath = os.path.join(self.imageDir, localName)
		if os.path.exists(localPath):
			print("image found locally")
			return Image.open(localPath)
		else:
			print("image being requested")
			response = requests.get(url)
			if response.status_code == 200:
				imgData = response.content
				self.store_image_local(localName, imgData)
				return Image.open(BytesIO(imgData))
		return None	
			
	def store_image_local(self, localName, imageData):
		localPath = os.path.join(self.imageDir, localName)
		with open(localPath, 'wb') as f:
			f.write(imageData)
		print("image stored locally")
		
	def gen_local_name(self, url):
		songCode = url.split('/')[-1] # last index of url split on /
		name = f"{songCode}.png"
		return name
	
	def create_buttons(self):
		self.startButton = Button(self.root, text="Start", command=self.start_track)
		self.startButton.pack(pady=10)
		
		# hold play back buttons
		self.buttonBar = Frame(self.root)
		self.buttonBar.pack(pady=10)
		
		self.previousButton = Button(self.buttonBar, image=self.previousPhoto,
									command=self.previous,
									borderwidth=0,
									highlightthickness=0,
									relief='flat',
									bg=self.root.cget('bg'),
									activebackground=self.root.cget('bg'),
									activeforeground=self.root.cget('bg'))
		self.previousButton.pack(padx=10, side=LEFT)
		
		self.playbackButton = Button(self.buttonBar, image=self.stopPhoto,
									command=self.set_playback,
									borderwidth=0,
									highlightthickness=0,
									relief='flat',
									bg=self.root.cget('bg'),
									activebackground=self.root.cget('bg'),
									activeforeground=self.root.cget('bg')) # play/pause button
		self.playbackButton.pack(padx=10, side=LEFT)
		
		self.nextButton = Button(self.buttonBar, image=self.nextPhoto,
									command=self.next,
									borderwidth=0,
									highlightthickness=0,
									relief='flat',
									bg=self.root.cget('bg'),
									activebackground=self.root.cget('bg'),
									activeforeground=self.root.cget('bg'))
		self.nextButton.pack(padx=10, side=LEFT)
		
		self.volumeSlider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL)
		self.volumeSlider.pack(pady=10)
		self.volumeSlider.bind("<ButtonRelease-1>", self.set_volume) # bound to reduce calls to spotify - only change when movement done
		self.volumeSlider.bind("<Button-1>", lambda event: self.volChange.set(True)) # block system moving slider
		
		self.currentTrack = Label(self.root, text="No track playing")
		self.currentTrack.pack(pady=10)
		
		self.imageFrame = Frame(self.root)
		self.imageFrame.pack(pady=10)
		
		self.previousImageLabel = Label(self.imageFrame, image=self.defaultPhotoSmall)
		self.previousImageLabel.pack(padx=40, side=LEFT)
		
		self.trackImage = Label(self.imageFrame, image=self.defaultPhoto)
		self.trackImage.pack(padx=20, side=LEFT)
		
		self.nextImageLabel = Label(self.imageFrame, image=self.defaultPhotoSmall)
		self.nextImageLabel.pack(padx=40, side=LEFT)
		
		# hold timing bar and labels
		self.progressBar = Frame(self.root)
		self.progressBar.pack(pady=10)
		
		self.currentLabel = Label(self.progressBar, text="--:--")
		self.currentLabel.pack(padx=10, side=LEFT)
		
		self.songProgress = ttk.Progressbar(self.progressBar, orient=HORIZONTAL, length=400, mode='determinate')
		self.songProgress.pack(padx=10, side=LEFT)
		self.songProgress.bind("<ButtonRelease-1>", self.user_seek)
		
		self.durationLabel = Label(self.progressBar, text="--:--")
		self.durationLabel.pack(padx=10, side=LEFT)

	def start_track(self):
		self.player.play_track_from_URI()
		
	def set_playback(self): # set play or pause
		if self.reply is not None:
			if self.reply['playing']:
				self.player.pause()
			else:
				self.player.resume()
	
	def previous(self):
		self.player.play_previous()

	def next(self):
		self.player.play_next()
		
	def set_volume(self, volume):
		level = self.volumeSlider.get()
		self.player.set_Vol(level)
		self.volChange.set(False)  
	
	def user_seek(self, event):
		if self.reply is not None:
			progWidth = self.songProgress.winfo_width() # progress bar size
			mousePos = event.x # click location
			newPosition = (mousePos/progWidth) * self.reply['length']
			self.player.seek(int(newPosition))
	
	def ms_to_minutes(self, time):
		totalSeconds = time / 1000
		minutes = int(totalSeconds // 60)
		seconds = int(totalSeconds % 60)
		if seconds < 10:
			seconds =  "0" + str (seconds)
		return f"{minutes}:{seconds}"		
	
	def request_status(self):
		try:
			self.reply = self.player.get_current_state()
			if self.reply is not None: # none will return if no song or device is found
				self.currentTrack.config(text=self.reply['name'])
				self.songProgress['maximum'] = self.reply['length']
				self.songProgress['value'] = self.reply['currentTime']
				self.durationLabel.config(text=self.ms_to_minutes(self.reply['length']))
				self.currentLabel.config(text=self.ms_to_minutes(self.reply['currentTime']))
				
				if not self.volChange.get(): # check to see if the user is changing volume
					self.volumeSlider.set(self.reply['volume']) # take volume from api
				
				if self.reply['playing']:
					self.playbackButton.config(image=self.pausePhoto)
				else:
					self.playbackButton.config(image=self.playPhoto)
				
				
				# -----
				# image loading
				# -----
				
				if self.reply['imgURL']: # image url for current song
					if self.reply['imgURL'] != self.currentImgURL: #song changed
						print("song changed")
						if self.currentImgURL is not None: # there is something at current
							# set previous to
							print("prev using old")
							curImg = self.load_image(self.currentImgURL).resize((100, 100), Image.Resampling.LANCZOS)
							curPhoto = ImageTk.PhotoImage(curImg)
							self.previousImageLabel.config(image=curPhoto)
							self.previousImageLabel.image = curPhoto
						else:
							self.previousImageLabel.config(image=self.defaultPhotoSmall)
						
						curImg = self.load_image(self.reply['imgURL']).resize((200, 200), Image.Resampling.LANCZOS)
						curPhoto = ImageTk.PhotoImage(curImg)
						self.trackImage.config(image=curPhoto)
						self.trackImage.image = curPhoto
						
						self.currentImgURL = self.reply['imgURL'] # store the url info

				else:
					self.trackImage.config(image=self.defaultPhoto)
					
				if self.reply['nextURL'] != self.nextImgURL: # next in queue changed
					if self.reply['nextURL'] is not None: # valid next in queue	
						# load check here -- returns image.open
						self.nextImgURL = self.reply['nextURL']
						curImg = self.load_image(self.nextImgURL).resize((100, 100), Image.Resampling.LANCZOS)
						curPhoto = ImageTk.PhotoImage(curImg)
						self.nextImageLabel.config(image=curPhoto)
						self.nextImageLabel.image = curPhoto
					else:
						self.nextImageLabel.config(image=self.defaultPhotoSmall)			
					
			else: # action for no track/device
				self.currentTrack.config(text="No track playing")
				self.songProgress['maximum'] = 0
				self.songProgress['value'] = 0
				self.playbackButton.config(image=self.stopPhoto)
				self.durationLabel.config(text="--:--")
				self.currentLabel.config(text="--:--")
				self.trackImage.config(image=self.defaultPhoto)
				self.previousImageLabel.config(image=self.defaultPhotoSmall)
				self.nextImageLabel.config(image=self.defaultPhotoSmall)
		except Exception as e:
			print(e)
		self.root.after(self.updateInterval, self.request_status) # call function every second
		
if __name__ == "__main__":
	root = Tk()
	app = piplayerGUI(root)
	root.geometry("900x900+25+25")
	root.mainloop()
