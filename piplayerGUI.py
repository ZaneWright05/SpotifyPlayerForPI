from tkinter import *
from tkinter import ttk
from piplayerCore import piplayerCore

class piplayerGUI:
	def __init__(self,root):
		self.root = root
		self.root.title("piplayer")
		self.player = piplayerCore()
		
		self.create_buttons()
		self.request_status()
	def create_buttons(self):
		self.startButton = Button(self.root, text="Start", command=self.start_track)
		self.startButton.pack(pady=10)
		
		self.playButton = Button(self.root, text="Play", command=self.play_track)
		self.playButton.pack(pady=10)
		
		self.pauseButton = Button(self.root, text="Pause", command=self.pause_track)
		self.pauseButton.pack(pady=10)
		
		self.volumeSlider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, command=self.set_volume)
		self.volumeSlider.pack(pady=10)
		
		self.currentTrack = Label(self.root, text="No track playing")
		self.currentTrack.pack(pady=10)
		
		self.songProgress = ttk.Progressbar(self.root, orient=HORIZONTAL, length=400, mode='determinate')
		self.songProgress.pack(pady=10)
		
	def play_track(self):
		self.player.resume()
		
	def start_track(self):
		self.player.play_track_from_URI()
		
	def pause_track(self):
		self.player.pause()
	
	def set_volume(self, volume):
		level = self.volumeSlider.get()
		print(level)
		self.player.set_Vol(level)
		
	def request_status(self):
		reply = self.player.get_current_state()
		if reply is not None:
			self.currentTrack.config(text=reply['name'])
			self.songProgress['maximum'] = reply['length']
			self.songProgress['value'] = reply['currentTime']
		else:
			self.currentTrack.config(text="No track playing")
			self.songProgress['maximum'] = 0
			self.songProgress['value'] = 0
		self.root.after(1000, self.request_status)
if __name__ == "__main__":
	root = Tk()
	app = piplayerGUI(root)
	root.geometry("900x900+25+25")
	root.mainloop()
