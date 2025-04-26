import yt_dlp
from asyncio import to_thread

async def import_youtube_playlist(url, output_folder):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'ignoreerrors': True,
        'noplaylist': False,
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
    }

    def run_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    await to_thread(run_download)
