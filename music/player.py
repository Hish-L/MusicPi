import asyncio
import os
import glob
import random
import discord
from utils.embed import send_paginated_embed
from discord.ext import commands
from music.ytdl import download_audio_streaming

class MusicPlayer:
    def __init__(self, bot, ctx):
        self.bot = bot
        self.queue = asyncio.Queue()
        self.current = None
        self.vc = None
        self.ctx = ctx
        self.guild_id = ctx.guild.id
        self.playing_task = None
        self.volume = 0.05

    def set_volume(self, value):
        self.volume = value
        if self.vc and self.vc.source:
            self.vc.source.volume = value

    async def queue_song(self, ctx, search):
        count = 0
        async for source in download_audio_streaming(search):
                await self.queue.put(source)
                count += 1

                if count == 1 and (not self.playing_task or self.playing_task.done()):
                        self.playing_task = self.bot.loop.create_task(self.play_loop())

        await ctx.send(f"✅ Queued {count} track(s) for '{search}'")

    async def play_loop(self):
        self.vc = await self.ctx.author.voice.channel.connect()
        while not self.queue.empty():
            self.current = await self.queue.get()
            ffmpeg_audio = discord.FFmpegPCMAudio(self.current)
            source = discord.PCMVolumeTransformer(ffmpeg_audio, volume=self.volume)
            self.vc.play(source, after=lambda e: print(f"Done: {e}"))
            while self.vc.is_playing():
                await asyncio.sleep(1)
        await self.vc.disconnect()

    async def skip_song(self, ctx):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            await ctx.send("Skipped current song.")

    async def show_queue(self, ctx):
        items = list(self.queue._queue)
        if not items:
            await ctx.send("Queue is empty.")
        else:
            msg = "\n".join(os.path.basename(i) for i in items)
            await ctx.send(f"Current queue:\n{msg}")

    async def show_queue_paginated(self, ctx):
        items = list(self.queue._queue)

        if not self.current and not items:
            await ctx.send("🎶 Nothing is currently playing or queued.")
            return

        now_playing = f"▶ **Now Playing:** `{os.path.basename(self.current)}`\n" if self.current else ""

        if not items:
            await ctx.send(now_playing + "Queue is empty.")
            return

        entries = [f"{i + 1}. {os.path.basename(item)}" for i, item in enumerate(items)]
        await send_paginated_embed(ctx, title="🎵 Current Queue", entries=entries, per_page=10)

    async def shuffle_queue(self, ctx):
        if self.queue.empty():
            await ctx.send("🔁 Queue is empty — nothing to shuffle.")
            return

        # Extract items from queue
        items = list(self.queue._queue)
        random.shuffle(items)

        # Recreate queue with shuffled items
        self.queue = asyncio.Queue()
        for item in items:
            await self.queue.put(item)

        await ctx.send("🔀 Shuffled queue.")

    async def queue_local_playlist(self, ctx, playlist_name):
        path = f"playlists/{playlist_name}"
        if not os.path.isdir(path):
            await ctx.send(f"❌ Playlist '{playlist_name}' not found.")
            return

        files = sorted(glob.glob(os.path.join(path, "*.*")))
        if not files:
            await ctx.send(f"⚠️ Playlist '{playlist_name}' is empty.")
            return

        for i, file in enumerate(files):
            await self.queue.put(file)
            if i == 0 and (not self.playing_task or self.playing_task.done()):
                self.playing_task = self.bot.loop.create_task(self.play_loop())

        await ctx.send(f"🎶 Queued {len(files)} track(s) from playlist '{playlist_name}'")

    async def stop(self, ctx):
        if self.vc:
            await self.vc.disconnect()
        self.queue = asyncio.Queue()
        await ctx.send("Stopped playback and cleared queue.")