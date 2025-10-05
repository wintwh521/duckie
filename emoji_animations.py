import discord
from discord.ext import commands
import re
import aiohttp
from io import BytesIO
from PIL import Image

# Regex to extract custom emoji format: <:name:id> or <a:name:id>
CUSTOM_EMOJI_REGEX = r"<(a?):(\w+):(\d+)>"

async def download_emoji(emoji_id: str, animated: bool):
    ext = "gif" if animated else "png"
    url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=128"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return BytesIO(await resp.read())
    return None

def spin_frames(img):
    frames = []
    for angle in range(0, 360, 20):
        rotated = img.rotate(angle, resample=Image.BICUBIC, expand=True)
        frames.append(rotated)
    return frames

def wiggle_frames(img):
    frames = []
    offsets = [-5, 5, -5, 5]
    for offset in offsets:
        frame = Image.new("RGBA", img.size)
        frame.paste(img, (offset, 0))
        frames.append(frame)
    return frames

def bounce_frames(img):
    frames = []
    offsets = [-5, 5, -5, 5]
    for offset in offsets:
        frame = Image.new("RGBA", img.size)
        frame.paste(img, (0, offset))
        frames.append(frame)
    return frames

def flip_frames(img):
    return [img, img.transpose(Image.FLIP_TOP_BOTTOM)]

async def process_and_send(ctx, emoji_match, frame_func, duration=50):
    animated, name, emoji_id = emoji_match.groups()
    img_bytes = await download_emoji(emoji_id, animated == "a")
    if not img_bytes:
        return await ctx.send("❌ Failed to download emoji.")

    img = Image.open(img_bytes).convert("RGBA")
    frames = frame_func(img)

    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration,
        transparency=0,
        disposal=2
    )
    output.seek(0)

    await ctx.send(file=discord.File(output, filename=f"{name}_anim.gif"))

def setup_emoji_commands(bot: commands.Bot):
    @bot.command(name="spin")
    async def spin(ctx, emoji: str):
        match = re.search(CUSTOM_EMOJI_REGEX, emoji)
        if not match:
            return await ctx.send("❌ Please use a custom emoji like `<:name:id>`.")
        await process_and_send(ctx, match, spin_frames)

    @bot.command(name="wiggle")
    async def wiggle(ctx, emoji: str):
        match = re.search(CUSTOM_EMOJI_REGEX, emoji)
        if not match:
            return await ctx.send("❌ Please use a custom emoji like `<:name:id>`.")
        await process_and_send(ctx, match, wiggle_frames)

    @bot.command(name="bounce")
    async def bounce(ctx, emoji: str):
        match = re.search(CUSTOM_EMOJI_REGEX, emoji)
        if not match:
            return await ctx.send("❌ Please use a custom emoji like `<:name:id>`.")
        await process_and_send(ctx, match, bounce_frames)

    @bot.command(name="flip")
    async def flip(ctx, emoji: str):
        match = re.search(CUSTOM_EMOJI_REGEX, emoji)
        if not match:
            return await ctx.send("❌ Please use a custom emoji like `<:name:id>`.")
        await process_and_send(ctx, match, flip_frames)
