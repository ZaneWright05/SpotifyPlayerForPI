from tkinter import *
from tkinter import ttk
from piplayerCore import piplayerCore
from PIL import Image, ImageTk
import os

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
		
		self.create_buttons()
		self.updateInterval = 500
		self.volChange = BooleanVar(value=False)
		self.reply = None # used to store song info - reduce calls
		self.request_status()
		
	def create_buttons(self):
		self.startButton = Button(self.root, text="Start", command=self.start_track)
		self.startButton.pack(pady=10)
		
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
		
		self.songProgress = ttk.Progressbar(self.root, orient=HORIZONTAL, length=400, mode='determinate')
		self.songProgress.pack(pady=10)
		self.songProgress.bind("<ButtonRelease-1>", self.user_seek)
		
	def previous_track(self):
		self.player.resume()
		
	def next_track(self):
		self.player.pause()

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
			
	def request_status(self):
		try:
			self.reply = self.player.get_current_state()
			if self.reply is not None: # none will return if no song or device is found
				self.currentTrack.config(text=self.reply['name'])
				self.songProgress['maximum'] = self.reply['length']
				self.songProgress['value'] = self.reply['currentTime']
				if not self.volChange.get(): # check to see if the user is changing volume
					self.volumeSlider.set(self.reply['volume']) # takes volume from api
				if self.reply['playing']:
					self.playbackButton.config(image=self.pausePhoto)
				else:
					self.playbackButton.config(image=self.playPhoto)
			else: # action for no track/device
				self.currentTrack.config(text="No track playing")
				self.songProgress['maximum'] = 0
				self.songProgress['value'] = 0
		except Exception as e:
			print(e)
		self.root.after(self.updateInterval, self.request_status) # call function every second
		
if __name__ == "__main__":
	root = Tk()
	app = piplayerGUI(root)
	root.geometry("900x900+25+25")
	root.mainloop()
