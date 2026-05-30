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
            parts = line.split()
            if len(parts) >= 2:
                ids.add(parts[1])
    return ids

def append_download_log(log_path, info_dict):
    """
    Save download information to a separate log file.

    Args:
        log_path (str): Path to log file.
        info_dict (dict): yt-dlp metadata dictionary.
    """
    video_id = info_dict.get("id")
    title = info_dict.get("title")

    if not video_id or not title:
        return

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"youtube {video_id} | {title}\n")
