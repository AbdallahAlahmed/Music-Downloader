import tkinter as tk
from tkinter import messagebox

from src.downloader import MusicDownloader
# This class is responsible for creating the GUI for the YouTube Music Downloader application.
class DownloaderGUI:
    """GUI class for the YouTube Music Downloader application."""
    def __init__(self):
        self.downloader = MusicDownloader()

        self.root = tk.Tk()
        self.root.title("YouTube Music Downloader")
        
        self.root.geometry("700x200")
        self.url_label = tk.Label(self.root, text="Enter the YouTube playlist URL:")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(self.root, width=80)
        self.url_entry.pack()
        self.download_button = tk.Button(self.root, text="Download playlist", command=self.download)
        self.download_button.pack(pady=20)
    
    def download(self):
        """
        Starts the download process for the playlist URL entered by the user.
        """
        # Get the playlist URL from the entry widget and start the download process.
        url = self.url_entry.get().strip()
        # Validate the URL before starting the download process.
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube playlist URL.")
            return
        # Call the download_playlist method of the MusicDownloader class to start the download process.
        self.downloader.download_playlist(url)
        messagebox.showinfo("Finished", "Playlist downloaded successfully!")

    def run(self):

        self.root.mainloop()