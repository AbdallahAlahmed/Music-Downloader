from src.downloader import download_music_playlist

if __name__ == "__main__":
    url = input("Enter playlist URL: ")
    download_music_playlist(url)
