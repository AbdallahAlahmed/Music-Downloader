
from src.downloader import MusicDownloader


def main():

    playlist_url = input(
        "Enter the YouTube playlist URL: "
    )

    downloader = MusicDownloader()

    downloader.download_playlist(playlist_url)


if __name__ == "__main__":
    main()
