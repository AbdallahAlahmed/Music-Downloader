import tkinter as tk

# This class is responsible for creating the GUI for the YouTube Music Downloader application.
class DownloaderGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube Music Downloader")
        
        self.root.geometry("600x200")

    def run(self):

        self.root.mainloop()