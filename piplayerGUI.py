from tkinter import *
from tkinter import ttk
from tkinter import font as tkfont
from piplayerCore import piplayerCore
from PIL import Image, ImageTk, ImageFilter
import os
import json
import requests
from io import BytesIO

class songWidget(Frame):
	def __init__(self, playerGUI, root, songInfo, defaultImg):
		Frame.__init__(self,root, bd=1, relief=RAISED)
		self.songURI = songInfo['uri']
		imageURL = songInfo['album']['images'][0]['url'] if songInfo['album']['images'] else None
		if imageURL is not None:
			songImage = playerGUI.load_image(imageURL).resize((50, 50), Image.Resampling.LANCZOS)
		else:
			songImage = defaultImg.resize((50, 50), Image.Resampling.LANCZOS)
			
		songPhoto = ImageTk.PhotoImage(songImage)
		
		name = songInfo['name']
		if len(name) > 15:
			name = name[:12] + "..."
		else:
			name = name.ljust(15)
		nameLabel = Label(self, text = name, font = tkfont.Font(family="Courier New", size=8))
		nameLabel.pack(side=LEFT, padx = 10)
		
		image = Label(self, image=songPhoto)
		image.image = songPhoto
		image.pack(side = LEFT, pady=10)
		
		duration = playerGUI.ms_to_minutes(songInfo['duration_ms'])
		lenLabel = Label(self, text = duration)
		lenLabel.pack(side = LEFT, pady=10)
	
	def get_uri(self):
			return self.songURI
			
class piplayerGUI:
	def __init__(self,root):
		self.flag = False
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
				
		self.create_widgets()
		self.updateInterval = 750
		self.volChange = BooleanVar(value=False)
		
		self.reply = None # used to store song info - reduce calls
		
		self.currentImgURL = None # used	
		self.nextImgURL = None
		
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
	
	def create_widgets(self):
		# ~ self.songEntry = Entry(width = 100)
		# ~ self.songEntry.pack(pady=10)
		self.mainFrame= Frame(self.root)
		self.mainFrame.pack(fill=BOTH, expand=True)

		self.playBackFrame = Frame(self.mainFrame)
		self.playBackFrame.pack(side=LEFT, fill=BOTH, expand=True)
		
		self.queueFrame = Frame(self.mainFrame, bg='blue')
		self.queueFrame.pack(side=RIGHT, fill=Y)
		
		self.queueCanvas = Canvas(self.queueFrame, bd=0, highlightthickness=0, width= 200)
		self.queueCanvas.pack(side=LEFT, fill=BOTH, expand=True)
		
		self.scrollBar = Scrollbar(self.queueFrame, orient=VERTICAL, command=self.queueCanvas.yview)
		self.scrollBar.pack(side=RIGHT, fill=Y)
		
		self.queueCanvas.configure(yscrollcommand=self.scrollBar.set)
		
		self.queueWidget = Frame(self.queueCanvas)
		self.queueCanvas.create_window((0,0), window=self.queueWidget, anchor='nw')

				
		self.queueWidget.bind("<Configure>", lambda e: self.queueCanvas.configure(scrollregion=self.queueCanvas.bbox("all")))

		
		# hold play back buttons
		self.buttonBar = Frame(self.playBackFrame)
		self.buttonBar.pack(pady=15)
		
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
		
		self.volumeSlider = Scale(self.playBackFrame, from_=0, to=100, orient=HORIZONTAL)
		self.volumeSlider.pack(pady=10)
		self.volumeSlider.bind("<ButtonRelease-1>", self.set_volume) # bound to reduce calls to spotify - only change when movement done
		self.volumeSlider.bind("<Button-1>", lambda event: self.volChange.set(True)) # block system moving slider
		
		self.currentTrack = Label(self.playBackFrame, text="No track playing")
		self.currentTrack.pack(pady=10)
		
		self.imageFrame = Frame(self.playBackFrame)
		self.imageFrame.pack(pady=10)
		
		self.previousImageLabel = Label(self.imageFrame, image=self.defaultPhotoSmall)
		self.previousImageLabel.pack(padx=40, side=LEFT)
		
		self.trackImage = Label(self.imageFrame, image=self.defaultPhoto)
		self.trackImage.pack(padx=20, side=LEFT)
		
		self.nextImageLabel = Label(self.imageFrame, image=self.defaultPhotoSmall)
		self.nextImageLabel.pack(padx=40, side=LEFT)
		
		# hold timing bar and labels
		self.progressBar = Frame(self.playBackFrame)
		self.progressBar.pack(pady=10)
		
		self.currentLabel = Label(self.progressBar, text="--:--")
		self.currentLabel.pack(padx=10, side=LEFT)
		
		self.songProgress = ttk.Progressbar(self.progressBar, orient=HORIZONTAL, length=400, mode='determinate')
		self.songProgress.pack(padx=10, side=LEFT)
		self.songProgress.bind("<ButtonRelease-1>", self.user_seek)
		
		self.durationLabel = Label(self.progressBar, text="--:--")
		self.durationLabel.pack(padx=10, side=LEFT)
		
		self.currentSongWidget = None
	
		# ~ self.queueWidget = Frame(self.root)
		# ~ self.queueWidget.pack(side=RIGHT, fill=Y, padx=10, pady=10)
		
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

	def update_song_queue(self, queue, currURI):
		first = None
		children = self.queueWidget.winfo_children()
		if children:
			first = children[0].get_uri()
		if currURI == first and first is not None: # next song is playing 		
			self.queueWidget.winfo_children()[0].destroy()
		else: # a different song has been seleted, queue changed 
			for widget in self.queueWidget.winfo_children():
				widget.destroy()
			for track in queue:
				sw = songWidget(self, self.queueWidget, track, self.defaultImage)
				sw.pack(expand=True, fill=X,side=TOP,pady=2)
			
			self.queueCanvas.configure(scrollregion=self.queueCanvas.bbox('all'))

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
						if self.currentSongWidget is not None:
							self.currentSongWidget.destroy()
						self.update_song_queue(self.reply['queue'], self.reply['currURI'])
						self.currentSongWidget = songWidget(self, self.playBackFrame, self.player.get_current_song(), self.defaultImage)
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
	root.geometry("1360x768+0+0")
	root.mainloop()
