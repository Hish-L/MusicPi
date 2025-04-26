import discord
import os
from utils.embed import send_paginated_embed
from utils.roles import is_dj
from utils.playlist_importer import import_youtube_playlist
from discord.ext import commands
from music.player import MusicPlayer

# Change this to restrict commands to
# single or multiple channels
# Leave empty if all channels are intended
ALLOWED_CHANNEL_IDS = [123456789012345678]
bot_token = "INSERT_BOT_TOKEN_HERE"

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = False

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

music_players = {}

def get_player(ctx):
    if ctx.guild.id not in music_players:
        music_players[ctx.guild.id] = MusicPlayer(bot, ctx)
    return music_players[ctx.guild.id]

@bot.check
async def only_allow_music_channel(ctx):
    if not ALLOWED_CHANNEL_IDS:
        return True  # ✅ no restriction, allow all channels

    if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
        await ctx.send("❌ This command can only be used in the music request channel.")
        return False

    return True

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.check(is_dj)
async def play(ctx, *, search: str):
    player = get_player(ctx)

    # Support: !play playlist <name>
    if search.lower().startswith(("playlist ", "pl ")):
        parts = search.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await ctx.send("❗ Usage: `!play playlist <name>` or `!play pl <name>`")
            return

        playlist_name = parts[1].strip()
        await player.queue_local_playlist(ctx, playlist_name)
        return

    # Otherwise: search or play YouTube
    await ctx.send(f"🔍 Searching and downloading '{search}'... hang tight!")
    await player.queue_song(ctx, search)

@bot.command()
@commands.check(is_dj)
async def volume(ctx, value: int):
    """Set playback volume (0–100%)"""
    if not 0 <= value <= 100:
        await ctx.send("❌ Volume must be between 0 and 100")
        return

    player = get_player(ctx)
    player.set_volume(value / 100)
    await ctx.send(f"🔉 Volume set to {value}%")

@bot.command(name="playlist", aliases=["pl"])
@commands.check(is_dj)
async def playlist(ctx, subcommand: str = None, name: str = None):
    playlists_path = "playlists"

    if subcommand is None:
        # List all available playlists
        if not os.path.isdir(playlists_path):
            await ctx.send("No playlists folder found.")
            return

        playlists = sorted(next(os.walk(playlists_path))[1])
        if not playlists:
            await ctx.send("No playlists available.")
        else:
            await ctx.send("📁 Available playlists:\n" + "\n".join(f"- `{p}`" for p in playlists))
        return

    # Handle: !playlist create <name>
    if subcommand == "create" and name:
        new_path = os.path.join(playlists_path, name)
        if os.path.exists(new_path):
            await ctx.send(f"⚠️ Playlist `{name}` already exists.")
        else:
            os.makedirs(new_path)
            await ctx.send(f"✅ Created new playlist: `{name}`")
        return

    # Handle: !playlist play <name>
    if subcommand == "play" and name:
        player = get_player(ctx)
        await player.queue_local_playlist(ctx, name)
        return

    # Handle: !playlist <name> → list files inside
    if subcommand and name is None:
        playlist_name = subcommand
        path = os.path.join(playlists_path, playlist_name)
        if not os.path.isdir(path):
            await ctx.send(f"❌ Playlist `{playlist_name}` not found.")
            return

        files = sorted(os.listdir(path))
        if not files:
            await ctx.send(f"📂 Playlist `{playlist_name}` is empty.")
            return

        entries = [f"- {os.path.splitext(f)[0]}" for f in files]
        await send_paginated_embed(ctx, title=f"Playlist: {playlist_name}", entries=entries)

        return
    
    # Handle: !playlist import <name> <url>
    if subcommand == "import" and name:
        args = ctx.message.content.strip().split()
        if len(args) < 4:
            await ctx.send("❌ Usage: `!playlist import <name> <YouTube playlist URL>`")
            return

        playlist_url = args[3]
        playlist_path = os.path.join(playlists_path, name)

        if not os.path.exists(playlist_path):
            await ctx.send(f"❌ Playlist `{name}` doesn't exist. Create it first using `!playlist create {name}`.")
            return

        await ctx.send(f"📥 Importing YouTube playlist into `{name}`... This may take a while. Check back with `!playlist {name}` later!")
        import asyncio
        asyncio.create_task(import_youtube_playlist(playlist_url, playlist_path))
        return
    
    # Handle: !playlist delete <name>
    if subcommand == "delete" and name:
        path = os.path.join(playlists_path, name)
        if not os.path.isdir(path):
            await ctx.send(f"❌ Playlist `{name}` doesn't exist.")
            return

        import shutil
        shutil.rmtree(path)
        await ctx.send(f"🗑️ Playlist `{name}` and all its files have been deleted.")
        return

    # If command doesn't match any pattern
    await ctx.send("❓ Invalid usage. Try:\n- `!playlist`\n- `!playlist create <name>`\n- `!playlist play <name>`\n- `!playlist <name>`")

@bot.command()
@commands.check(is_dj)
async def skip(ctx):
    player = get_player(ctx)
    await player.skip_song(ctx)

@bot.command()
@commands.check(is_dj)
async def queue(ctx):
    """Show the current queue with embed-based pagination"""
    player = get_player(ctx)
    await player.show_queue_paginated(ctx)

@bot.command()
@commands.check(is_dj)
async def shuffle(ctx):
    """Shuffle the current queue (excluding the playing song)"""
    player = get_player(ctx)
    await player.shuffle_queue(ctx)

@bot.command(name="stop", aliases=["leave", "quit", "disconnect", "exit"])
@commands.check(is_dj)
async def stop(ctx):
    player = get_player(ctx)
    await player.stop(ctx)

@bot.command(name="help")
async def help_command(ctx):
    help_text = """
🎵 **Music Bot Commands** 🎵

**Playback**
`!play <search or url>` — Search YouTube or play direct link
`!play playlist <name>` - Play a saved playlist  
`!skip` — Skip current song  
`!stop` — Stop and leave the voice channel  
`!queue` — Show currently queued songs
`!shuffle` - Shuffle currently queued songs  
`!volume <0–100>` — Set playback volume

**Playlists**
`!playlist` — List all saved playlists  
`!playlist create <name>` — Create a new playlist  
`!playlist play <name>` — Play a saved playlist
`!playlist import <name> <youtube_link>` - Add songs or list to playlist  
`!playlist <name>` — Show files in a playlist
`!playlist delete <name>` - Delete playlist and all its contents

**Other**
`!help` — Show this help message  
*All commands are restricted to users with the `DJ` role.*
"""
    await ctx.send(help_text)

bot.run(bot_token)
