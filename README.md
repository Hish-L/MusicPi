# 🎵 Discord Music Bot

A self-hosted Python music bot for Discord that:
- Searches YouTube for songs/playlists
- Downloads audio locally (to bypass YouTube's bot streaming restrictions)
- Streams audio to a voice channel from local files
- Supports YouTube playlists, local playlists, queueing, shuffling, and DJ role permissions

---

## 🚀 Features

- `!play <query | YouTube URL>`: Search or play a song or playlist
- `!queue`: Paginated view of queued songs
- `!skip`, `!stop`, `!volume <0-100>`: Core playback controls
- `!playlist`: 
  - `!playlist` → List available local playlists
  - `!playlist create <name>` → Create a new playlist folder
  - `!playlist play <name>` → Play all audio files in a playlist
  - `!playlist <name>` → Paginated listing of tracks in a playlist
  - `!playlist import <name> <YouTube Playlist URL>` → Import YouTube playlist into local folder
  - `!playlist delete <name>` → Delete a playlist folder
- `!shuffle`: Shuffles the remaining songs in the queue
- Role-restricted: only users with the `DJ` role can control the bot

---

## 📦 Requirements

- Python 3.10+
- ffmpeg
- Discord bot token
- A Raspberry Pi or Linux machine (or any server)

---

## 🛠 Setup Instructions

1. **Clone the repo**

```bash
git clone https://github.com/yourusername/discord-music-bot.git
cd discord-music-bot
```

2. **Install dependencies**

```bash
sudo apt update
sudo apt install -y ffmpeg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> If `requirements.txt` doesn't exist yet, use:

```
discord.py
yt-dlp
pynacl
```

3. **Set your bot token**

Edit `bot.py` and replace:

```python
bot.run("YOUR_BOT_TOKEN")
```

with your actual Discord bot token.

4. **Run the bot**

```bash
python bot.py
```

---

## 💡 Running as a Service (Linux systemd)

1. Create a service file:

```bash
sudo nano /etc/systemd/system/musicbot.service
```

Paste this:

```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/musicbot
ExecStart=/home/pi/musicbot/venv/bin/python /home/pi/musicbot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

> Adjust paths as needed (e.g. if you're not using user `pi`)

2. Enable and start:

```bash
sudo systemctl daemon-reexec
sudo systemctl enable musicbot
sudo systemctl start musicbot
```

3. Check logs:

```bash
journalctl -u musicbot -f
```

---

## 🗃 Folder Structure

```
.
├── bot.py                     # Main command handler
├── music/
│   ├── player.py              # Playback & queue management
│   └── ytdl.py                # YouTube downloader (yt-dlp)
├── utils/
│   ├── roles.py               # DJ role check
│   ├── embed.py               # Embed pagination helper
│   └── playlist_importer.py   # Background playlist importer
├── playlists/                 # Local playlists go here
└── data/                      # Temporary downloaded files from YouTube
```

---

## 📄 License

MIT — use, modify, and self-host freely.
