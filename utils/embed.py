# utils/embed.py
import discord
import asyncio

async def send_paginated_embed(ctx, title, entries, per_page=20):
    pages = [entries[i:i + per_page] for i in range(0, len(entries), per_page)]
    total_pages = len(pages)

    def create_embed(page_index):
        embed = discord.Embed(title=title, description="\n".join(pages[page_index]), color=discord.Color.blurple())
        embed.set_footer(text=f"Page {page_index + 1} of {total_pages}")
        return embed

    current = 0
    message = await ctx.send(embed=create_embed(current))
    user = ctx.author

    if total_pages <= 1:
        return

    emojis = ["⏮", "⏪", "▶", "⏩", "⏭"]
    for emoji in emojis:
        await message.add_reaction(emoji)

    def check(reaction, user_reacted):
        return user_reacted == user and str(reaction.emoji) in emojis and reaction.message.id == message.id

    while True:
        try:
            reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=120.0, check=check)
            emoji = str(reaction.emoji)

            if emoji == "⏮":
                current = 0
            elif emoji == "⏪":
                current = max(0, current - 1)
            elif emoji == "▶":
                break
            elif emoji == "⏩":
                current = min(total_pages - 1, current + 1)
            elif emoji == "⏭":
                current = total_pages - 1

            await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)

        except asyncio.TimeoutError:
            break

    await message.clear_reactions()
