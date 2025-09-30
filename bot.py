import discord
from discord.ext import commands
import re
import os
import requests
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

"""
@bot.command(name='help')
async def help_command(ctx):
    await ctx.send('just a duckie~')
"""


@bot.command(name='help', help="Shows this help message.")
async def help_command(ctx):
    await ctx.send("just a duckie~")
    
    embed = discord.Embed(title="Help - List of Commands", color=discord.Color.blue())

    for command in bot.commands:
        if not command.hidden:  # Skip commands marked hidden
            # command.help can be None if not set, so use fallback text
            description = command.help or "No description provided."
            embed.add_field(name=f"%{command.name}", value=description, inline=False)

    await ctx.send(embed=embed)


@bot.command(name='joke', help="Get a random joke to brighten your day.")
async def joke_command(ctx):
    try:
        response = requests.get('https://v2.jokeapi.dev/joke/Any?type=single')
        data = response.json()
        joke = data.get('joke', 'Oops! No joke found this time.')
        await ctx.send(joke)
    except Exception as e:
        await ctx.send("Sorry, I couldn't fetch a joke right now.")
        print(f"Joke API error: {e}")


@bot.command(name='dame', help='DAME!')
async def sticker_command(ctx):
    sticker_id = 1420011438084194324
    url = f"https://cdn.discordapp.com/stickers/{sticker_id}.png"
    embed = discord.Embed()
    embed.set_image(url=url)
    try:
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("Oops, I couldn't send the sticker!")
        print(f"Sticker error: {e}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    custom_emoji_pattern = r'<(a?):(\w+):(\d+)>'
    custom_emojis = re.findall(custom_emoji_pattern, message.content)

    if custom_emojis:
        for animated, name, emoji_id in custom_emojis:
            ext = 'gif' if animated else 'png'
            url = f'https://cdn.discordapp.com/emojis/{emoji_id}.{ext}?size=128'
            embed = discord.Embed()
            embed.set_image(url=url)
            await message.channel.send(embed=embed)


# -------------------
# ✅ KEEP-ALIVE SERVER
# -------------------

app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run_web():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.start()


# -------------------
# ✅ START BOT
# -------------------

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if TOKEN:
    keep_alive()
    bot.run(TOKEN)
else:
    print('ERROR: DISCORD_BOT_TOKEN not found in environment variables')
    print(
        'Please set your Discord bot token using the DISCORD_BOT_TOKEN secret')
