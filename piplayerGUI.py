from tkinter import *
from piplayerCore import piplayerCore

class piplayerGUI:
	def __init__(self,root):
		self.root = root
		self.root.title("piplayer")
		self.player = piplayerCore()
		
		self.create_buttons()
		
	def create_buttons(self):
		self.startButton = Button(self.root, text="Start", command=self.start_track)
		self.startButton.pack()
		
		self.playButton = Button(self.root, text="Play", command=self.play_track)
		self.playButton.pack()
		
		self.pauseButton = Button(self.root, text="Pause", command=self.pause_track)
		self.pauseButton.pack()
		
		self.volumeSlider = Scale(self.root, from_=0, to=100, orient=HORIZONTAL, command=self.set_volume)
		self.volumeSlider.pack()
		
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
		
if __name__ == "__main__":
	root = Tk()
	app = piplayerGUI(root)
	root.geometry("300x300+25+25")
	root.mainloop()
