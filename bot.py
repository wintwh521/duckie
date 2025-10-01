import discord
from discord.ext import commands
import re
import os
import random
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


@bot.command(name='ask', help='Ask the duckie anything - no guarantees you’ll like the answer.')
async def ask_command(ctx, *, question: str):
    responses = [
        "Hmm, interesting question. I'll have to think about that.",
        "That's a tough one. Let me consult my quackbook.",
        "Maybe. Maybe not. Maybe you should ask again later.",
        "I'm just a duck, not a fortune teller. But hey, maybe.",
        "Ask again when the moon is full and you're wearing a hat.",
        "The answer is hidden in the depths of my pond. Good luck finding it.",
        "Probably not. But who knows, right?",
        "Yes, but only if you promise to feed me afterwards.",
        "Definitely. I'm a duck, I know things.",
        "No way, Jose. Unless you're asking about quacking.",
        "Maybe. But only if you promise to be my friend.",
        "Ask again when the stars align. Or not, I don't know astrology.",
        "I'm not sure, but I'm sure you'll figure it out.",
        "Yes, but only if you promise to sing me a song.",
        "Ask again when the sun is in Leo.",
        "Probably. But only if you promise to share your snacks with me.",
        "Maybe. But only if you promise to be my best friend.",
        "Ask again when the moon is in Taurus.",
        "Quek Quek~",
        "Oh wow, what a *totally* original question. 🙄",
        "I'm just a duck. You expect me to know *that*?",
        "Sounds like a tomorrow problem. Or never. Probably never.",
        "I'll pretend I didn't hear that. For both our sakes.",
        "You're asking **me**? Bold of you to assume I care.",
        "That’s above my pay grade. I work for crumbs.",
        "The answer is... buried in the sands of time. Good luck.",
        "Have you tried Googling it like a normal person?",
        "If I had a coin for every time someone asked that... I'd still be broke.",
        "You know what? Yes. Just yes.",
        "I could answer, but then I'd have to delete you.",
        "You want answers? I want snacks. We all have dreams.",
        "Interesting question. Here's a better one: Why are you like this?",
        "I'm a duck, not a therapist. Though I *am* judging you.",
        "Let me consult the Oracle of Quack... nope, nothing.",
        "Try shaking your device. Sometimes that helps. Not here, though.",
        "42. Still 42. Always 42.",
        "That question gave me a headache.",
        "I'm telling the FBI you asked that.",
        "Even ChatGPT wouldn’t touch that one. And they let *me* talk.",
        "Why don’t you ask your mom? Oh wait, she sent me the same question.",
        "Wow, just wow. You really asked that out loud.",
        "My circuits are crying.",
        "BRB, updating my life choices after hearing that.",
        "Ask me again and I’ll pretend to crash.",
        "You know the answer. Deep down. Probably not, though.",
        "Is this a riddle? Or just nonsense?",
        "Duck mode activated: 🦆 No clue. Bye.",
        "Wow, deep. Let me go contemplate my pond.",
        "Sorry, I'm currently out of sarcasm. Please try again later.",
        "I'll need at least 3 lattes to process that question.",
    ]
    response = random.choice(responses)
    await ctx.send(response)


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
