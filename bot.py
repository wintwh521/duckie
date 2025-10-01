import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime
from discord import TextChannel
import re
import os
import random
import requests
import difflib
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
    birthday_check.start()


"""
@bot.command(name='help')
async def help_command(ctx):
    await ctx.send('just a duckie~')
"""


@bot.command(name='help', help="Shows this help message.")
async def help_command(ctx):
    await ctx.send("just a duckie~")

    embed = discord.Embed(title="Help - List of Commands",
                          color=discord.Color.blue())

    for command in bot.commands:
        if not command.hidden:  # Skip commands marked hidden
            # command.help can be None if not set, so use fallback text
            description = command.help or "No description provided."
            embed.add_field(name=f"%{command.name}",
                            value=description,
                            inline=False)

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

@bot.command(name='ask',help='Ask the duckie anything - no guarantees you’ll like the answer.')
async def ask_command(ctx, *, question: str):
    question = question.lower()

    categories = {
        "yes_no": {
            "keywords": [
                "is", "are", "was", "were", "do", "does", "can", "will", "should",
                "would", "have", "did", "could", "has", "had", "may", "might", "must"
            ],
            "responses": [
                "Yes. No. Maybe. I don't know. Can you repeat the question?",
                "Sure, but only if you do a little dance first.",
                "Probably, unless the ducks revolt.",
                "Nope. Not in this reality.",
                "Yes, but I won’t explain why. Deal with it.",
                "Definitely. Unless it isn't. Who knows?",
                "Ask your toaster. It's more qualified than I am.",
                "You should know better than to trust a duck's opinion.",
                "Yes, and also no. Enjoy the clarity.",
                "No. But say it with confidence and people will believe you."
            ]
        },
        "deep": {
            "keywords": [
                "meaning", "life", "love", "why", "purpose", "feel",
                "exist", "soul", "sad", "truth"
            ],
            "responses": [
                "Ah, the big questions. I’d answer, but then I’d have to cry.",
                "The meaning of life is snacks. All else is noise.",
                "You want purpose? I just want breadcrumbs.",
                "Love is like a goose — unpredictable and kinda terrifying.",
                "Existence is pain. Except for bubble tea.",
                "Some questions are better left unanswered. Like this one.",
                "I'm just a duck with Wi-Fi. Ask a therapist.",
                "You feel too much. Go touch grass or pet a cat.",
                "The truth is out there. Probably being ignored.",
                "I have no soul. Just sarcasm and feathers."
            ]
        },
        "silly": {
            "keywords": [
                "fart", "poop", "banana", "goose", "quack", "duck",
                "noodle", "joke", "meme", "lol"
            ],
            "responses": [
                "Quack quack... you summoned the nonsense lord?",
                "That question was so weird, even the goose stopped hissing.",
                "10/10. Would ask again just to confuse future AI archaeologists.",
                "You should write that down and never show anyone.",
                "Honestly? That made me laugh. And worry. Mostly worry.",
                "My circuits are overheating from secondhand embarrassment.",
                "Your brain is a beautiful mystery. Like expired yogurt.",
                "Congratulations. You've reached peak internet.",
                "Duck mode activated: 🦆 Processing nonsense... done.",
                "That belongs in a museum. Of cursed questions."
            ]
        },
        "tech": {
            "keywords": [
                "discord", "bot", "code", "python", "error", "ai",
                "server", "login", "bug", "crash"
            ],
            "responses": [
                "Did you try turning it off and on again?",
                "Sounds like a you problem. And by you, I mean the code.",
                "If it works, don’t touch it. If it doesn't, panic quietly.",
                "That's not a bug. It’s a feature. Probably.",
                "My only solution: Sacrifice a USB stick to the tech gods.",
                "Errors are just spicy warnings.",
                "This question requires admin privileges. Denied.",
                "Try blaming the intern. Always works.",
                "404: Helpful response not found.",
                "Crashes build character. And anxiety."
            ]
        },
        "food": {
            "keywords": [
                "eat", "food", "snack", "pizza", "bread", "cake", "cookie",
                "hungry", "drink", "coffee"
            ],
            "responses": [
                "Feed me and I might answer.",
                "Is this a bribe? Because it's working.",
                "I’m a duck. My entire life is about snacks.",
                "Pizza is love. Pizza is life.",
                "I’d do anything for cake. Anything.",
                "Forget your question — tell me what you're eating.",
                "Yes, I’ll take fries with that question.",
                "Caffeine makes the answers faster. But weirder.",
                "Ask again after snacks.",
                "The duck is hungry. The question can wait."
            ]
        },
        "default": {
            "keywords": [],
            "responses": [
                "Hmm, interesting question. I'll have to think about that.",
                "That's a tough one. Let me consult my quackbook.",
                "Maybe. Maybe not. Maybe you should ask again later.",
                "I'm just a duck, not a fortune teller. But hey, maybe.",
                "Ask again when the moon is full and you're wearing a hat.",
                "The answer is hidden in the depths of my pond. Good luck finding it.",
                "You're asking **me**? Bold of you to assume I care.",
                "That’s above my pay grade. I work for crumbs.",
                "If I had a coin for every time someone asked that... I'd still be broke.",
                "Why don’t you ask your mom? Oh wait, she sent me the same question.",
            ]
        }
    }

    best_match = "default"
    highest_score = 0

    for category, data in categories.items():
        for keyword in data["keywords"]:
            score = difflib.SequenceMatcher(None, question, keyword).ratio()
            if score > highest_score:
                highest_score = score
                best_match = category

    response = random.choice(categories[best_match]["responses"])
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


birthday_messages = [
    "🎉 Happy Birthday, {mention}! You're one year closer to becoming a Discord bot yourself.",
    "🥳 {mention}, congrats on surviving another trip around the sun!",
    "🎂 {mention}, may your day be filled with cake and lag-free games.",
    "🦆 {mention}, quack quack! It's your birthday! Waddle into greatness.",
    "🎈 {mention}, you leveled up! Still waiting for those patch notes though...",
    "🍰 Happy Birthday, {mention}! I didn't get you a gift, but I did remember. That counts, right?",
    "🎊 {mention}, it's your special day! Now act like it until midnight.",
    "😎 {mention}, you're older, wiser, and still hanging out with this bot. Love that for you.",
    "🎁 {mention}, another year older... still no legendary loot. Maybe next year.",
    "🐥 {mention}, birthdays are like bugs - they just keep coming. Enjoy the glitch!",
]

# 🎂 Hardcoded birthdays: user_id => "MM-DD"
birthdays = {
    507919534439530496: "05-21",
    914389664230699038: "01-04",
    591560009939288065: "09-02",
    1419926344111755274: "10-08"
}


@tasks.loop(hours=24)
async def birthday_check():
    today = datetime.now().strftime("%m-%d")
    channel = bot.get_channel(1419902888494239785)  #general-chat

    if channel is None:
        print("Birthday channel not found!")
        return

    for user_id, bday in birthdays.items():
        if bday == today:
            try:
                user = await bot.fetch_user(user_id)
                message = random.choice(birthday_messages).format(
                    mention=user.mention)
                #await channel.send(message)
                if isinstance(channel, TextChannel):
                    await channel.send(message)
                else:
                    print(
                        "Channel is not a text channel - cannot send message.")
            except Exception as e:
                print(f"Failed to send birthday message for {user_id}: {e}")


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
