import discord
from discord.ext import commands
import re
import os
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

@bot.command(name='help')
async def help_command(ctx):
    await ctx.send('just a duckie~')

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
    print('Please set your Discord bot token using the DISCORD_BOT_TOKEN secret')
