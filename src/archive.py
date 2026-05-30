import os


def load_download_archive_ids(archive_path):
    """
    Load all previously downloaded YouTube video IDs
    from the download archive file.

    Args:
        archive_path (str): Path to the archive file.

    Returns:
        set: Set containing downloaded video IDs.
    """
    ids = set()
    if not os.path.exists(archive_path):
        return ids

    with open(archive_path, "r", encoding="utf-8") as archive_file:
        for line in archive_file:
            line = line.strip()
            if not line:
                continue
            parts = line.split(maxsplit=2)
            if len(parts) >= 2:
                ids.add(parts[1])
    return ids

def append_archive_title(archive_path, info_dict):
    """
    Append downloaded video information
    to the archive log file.

    Args:
        archive_path (str): Path to archive file.
        info_dict (dict): yt-dlp metadata dictionary.
    """
    data = info_dict.get("id")
    if not data:        return
    video_id = info_dict.get("id")
    title = info_dict.get("title")
    if not video_id or title is None:
        return
    
    with open(archive_path, "a", encoding="utf-8") as archive_file:
        archive_file.write(f"youtube {video_id} | {title}\n")
