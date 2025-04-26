import os
import yt_dlp
from asyncio import to_thread
from yt_dlp.utils import DownloadError

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " -_").rstrip()

async def download_audio_streaming(search_query):
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Fetch metadata asynchronously
    def fetch_info():
        ydl_opts_info = {
            'quiet': True,
            'format': 'bestaudio/best',
            'noplaylist': False,
            'default_search': 'ytsearch',
        }
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            return ydl.extract_info(search_query, download=False)

    info = await to_thread(fetch_info)
    entries = info['entries'][:20] if 'entries' in info else [info]  # Limit to 20 entries

# Inside download_audio_streaming()

    for entry in entries:
        # Skip malformed entries
        if entry is None or 'title' not in entry or 'ext' not in entry or 'webpage_url' not in entry:
            continue

        try:
            title = sanitize_filename(entry.get('title', 'unknown'))
            file_path = os.path.join(output_dir, f"{title}.{entry['ext']}")

            if not os.path.exists(file_path):
                def do_download():
                    ydl_opts_download = {
                        'format': 'bestaudio/best',
                        'quiet': True,
                        'outtmpl': f'{output_dir}/{title}.%(ext)s',
                    }
                    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                        ydl.download([entry['webpage_url']])

                await to_thread(do_download)

            yield file_path

        except DownloadError as e:
            print(f"[Skipped] {entry.get('title', 'unknown')}: {e}")
            continue
        except Exception as e:
            print(f"[Error] {entry.get('title', 'unknown')}: {e}")
            continue
