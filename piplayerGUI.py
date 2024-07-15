from tkinter import *
from tkinter import ttk
from piplayerCore import piplayerCore

class piplayerGUI:
	def __init__(self,root):
		self.root = root
		self.root.title("piplayer")
		self.player = piplayerCore()
		
		self.create_buttons()
		self.updateInterval = 500
		self.volChange = BooleanVar(value=False)
		self.reply = None # used to store song info - reduce calls
		self.request_status()
		
	def create_buttons(self):
		self.startButton = Button(self.root, text="Start", command=self.start_track)
		self.startButton.pack(pady=10)
		
		self.playButton = Button(self.root, text="Play", command=self.play_track)
		self.playButton.pack(pady=10)
		
		self.pauseButton = Button(self.root, text="Pause", command=self.pause_track)
		self.pauseButton.pack(pady=10)
		
		self.volumeSlider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL)
		self.volumeSlider.pack(pady=10)
		self.volumeSlider.bind("<ButtonRelease-1>", self.set_volume) # bound to reduce calls to spotify - only change when movement done
		self.volumeSlider.bind("<Button-1>", lambda event: self.volChange.set(True)) # block system moving slider
		
		self.currentTrack = Label(self.root, text="No track playing")
		self.currentTrack.pack(pady=10)
		
		self.songProgress = ttk.Progressbar(self.root, orient=HORIZONTAL, length=400, mode='determinate')
		self.songProgress.pack(pady=10)
		self.songProgress.bind("<ButtonRelease-1>", self.user_seek)
		
	def play_track(self):
		self.player.resume()
		
	def start_track(self):
		self.player.play_track_from_URI()
		
	def pause_track(self):
		self.player.pause()
	
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
			else: # acion for no track/device
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
