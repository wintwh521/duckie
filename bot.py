import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from discord import TextChannel
import re
import os
import random
import requests
import difflib
import asyncio
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='%', intents=intents, help_command=None)

OWNER_ID = 507919534439530496
GENERAL_CHAT_CHANNEL_ID = 1419902888494239785

# -------------------
# ✅ BOT READY
# -------------------
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    birthday_check.start()
    bot.loop.create_task(post_random_quote())
    
    # Set the bot's presence to "Watching duck videos"
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="duck videos 🦆"
    )
    await bot.change_presence(activity=activity)


# -------------------
# %help
# -------------------
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


# -------------------
# %remindme
# -------------------
@bot.command(name="remindme")
@commands.is_owner()
async def remindme(ctx, date_part: str, time_part: str, *, reminder_message: str):
    """
    Reminder format:
    %remindme 2025-12-31 18:00 Happy New Year!
    """
    try:
        date_str = f"{date_part} {time_part}"
        
        # Parse the date_str into a datetime object
        reminder_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        # Calculate the time difference between now and the reminder time
        time_diff = reminder_time - datetime.now()

        # If the time has already passed, notify the user
        if time_diff.total_seconds() <= 0:
            await ctx.send("That time is in the past! Please set a future date.")
            return

        # Wait until the reminder time
        await asyncio.sleep(time_diff.total_seconds())

        channel = bot.get_channel(GENERAL_CHAT_CHANNEL_ID)
        
        if channel and isinstance(channel, discord.TextChannel):
            # Mention the owner in the message when the reminder time comes
            owner = await bot.fetch_user(OWNER_ID)  # Fetch the owner by user ID
            await channel.send(f"{owner.mention}, Reminder: {reminder_message}")
        else:
            print(f"Channel with ID {GENERAL_CHAT_CHANNEL_ID} not found or is not a TextChannel.")

    except ValueError:
        await ctx.send("Please use the correct format for the date: `YYYY-MM-DD HH:MM`.")


# -------------------
# set bot's presence
# -------------------
@bot.command(name="setplaying")
@commands.is_owner()
async def set_playing(ctx, *, status_message: str):
    await bot.change_presence(activity=discord.Game(name=status_message))
    await ctx.send(f"Bot is now playing: {status_message}")


@bot.command(name="setlistening")
@commands.is_owner()
async def set_listening(ctx, *, status_message: str):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status_message))
    await ctx.send(f"Bot is now listening to: {status_message}")

@bot.command(name="setwatching")
@commands.is_owner()
async def set_watching(ctx, *, status_message: str):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_message))
    await ctx.send(f"Bot is now watching: {status_message}")


@bot.command(name="setstreaming")
@commands.is_owner()
async def set_streaming(ctx, url: str, *, status_message: str):
    await bot.change_presence(activity=discord.Streaming(name=status_message, url=url))
    await ctx.send(f"Bot is now streaming: {status_message}")


# -------------------
# %joke
# -------------------
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


# -------------------
# %dame
# -------------------
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


# -------------------
# %ask
# -------------------
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


# -------------------
# enlarge emojis
# -------------------
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
# random quotes
# -------------------
quotes = [
    "“The only limit to our realization of tomorrow is our doubts of today.” – Franklin D. Roosevelt",
    "“In the end, we will remember not the words of our enemies, but the silence of our friends.” – Martin Luther King Jr.",
    "“Life is 10% what happens to us and 90% how we react to it.” – Charles R. Swindoll",
    "“It always seems impossible until it's done.” – Nelson Mandela",
    "“Believe you can and you're halfway there.” – Theodore Roosevelt",
    "“You must be the change you wish to see in the world.” – Mahatma Gandhi",
    "“The purpose of life is not to be happy. It is to be useful, to be honorable, to be compassionate, to have it make some difference that you have lived and lived well.” – Ralph Waldo Emerson",
    "“You only live once, but if you do it right, once is enough.” – Mae West",
    "“In three words I can sum up everything I've learned about life: it goes on.” – Robert Frost",
    "“Life is really simple, but we insist on making it complicated.” – Confucius",

    # Funny & Random Quotes:
    "“I’m not arguing, I’m just explaining why I’m right... in a very loud voice.” – Unknown",
    "“I could agree with you, but then we’d both be wrong.” – Unknown",
    "“If at first you don’t succeed, then skydiving is not for you.” – Unknown",
    "“Life is short. Smile while you still have teeth.” – Unknown",
    "“A day without laughter is a day wasted... unless you’re in a library.” – Unknown",
    "“I told my computer I needed a break, and now it won’t stop sending me ads for vacation packages.” – Unknown",
    "“I’m on a seafood diet. I see food and I eat it.” – Unknown",
    "“If you can’t remember my name, just say ‘hey you.’ I respond to that.” – Unknown",
    "“I’m multitasking: I can listen, ignore, and forget all at once.” – Unknown",
    "“The best way to predict the future is to create it… or just wing it.” – Unknown",

    # Silly and Absurd Quotes:
    "“I'm not procrastinating, I'm doing side quests.” – Unknown",
    "“I’m not a morning person. Or an afternoon person. Let’s be real — I’m barely a person.” – Unknown",
    "“I’m not weird, I’m just limited edition.” – Unknown",
    "“I would agree with you, but then we’d both be wrong.” – Unknown",
    "“If you don’t know where you’re going, any road will take you there. Or you can just get lost.” – Unknown",
    "“I’m on a coffee break. Which means I’m just looking for the coffee.” – Unknown",
    "“My wallet is like an onion, opening it makes me cry.” – Unknown",
    "“I am a work in progress... which is why I’m always late.” – Unknown",
    "“I’m reading a book on anti-gravity. It’s impossible to put down.” – Unknown",
    "“Sometimes I drink water to surprise my liver.” – Unknown",
    "“My phone autocorrects ‘ducking’ to ‘ducking’ and I think it’s a sign.” – Unknown",
    "“I wonder if clouds ever look down on us and say, ‘That one’s doing it wrong.’” – Unknown",
    "“I'm not short, I'm just concentrated awesome.” – Unknown",
    "“I’m on a seafood diet. I see food and I eat it.” – Unknown",
    "“I told my computer I needed a break, and now it keeps sending me ads for vacations.” – Unknown",
    "“I’m not weird, I’m just limited edition.” – Unknown",
    "“I am on a chocolate diet. I eat chocolate, and if I gain weight, I eat more chocolate.” – Unknown",
    "“I’d agree with you, but then we’d both be wrong.” – Unknown",
    "“I’m not lazy, I’m on energy-saving mode.” – Unknown",
    "“I don’t need an inspirational quote, I need coffee.” – Unknown",
    "“The only exercise I get is running out of time.” – Unknown",
    "“I used to think I was indecisive, but now I’m not so sure.” – Unknown",
    "“I'm like a cloud. When I disappear, it’s a beautiful day.” – Unknown",
    "“I’m not clumsy, I’m just on a quest to test the durability of objects.” – Unknown",
    "“The road to success is always under construction. So is my life.” – Unknown",
    "“Do you ever look at someone and wonder, ‘What is going on inside their head?’ Then realize it's just random thoughts about pizza?” – Unknown",
    "“I don’t know what I’m doing, but I’m doing it very well.” – Unknown",
    "“My imaginary friend says you have serious issues.” – Unknown",
    "“Life is short. Smile while you still have teeth.” – Unknown",
    "“I would tell you a joke about a pencil, but it’s pointless.” – Unknown",
    "“There are no mistakes in life, only happy little accidents. Like that time I accidentally locked myself out of my house in my underwear.” – Unknown",
    "“I’m on a 30-day diet. So far, I’ve lost 15 days.” – Unknown",
    "“Why do I never wake up early enough for breakfast? Because I’m a professional snoozer.” – Unknown",
    "“My wallet is like an onion, opening it makes me cry.” – Unknown",
    "“I am not a morning person. I’m barely a person, period.” – Unknown",
    "“I tried to be normal once. Worst two minutes ever.” – Unknown",
    "“I'm not arguing, I'm just explaining why I'm right... again.” – Unknown",
    "“Some days I amaze myself. Other days, I put my keys in the fridge.” – Unknown",
    "“I’m not saying I’m Batman, but have you ever seen me and Batman in the same room?” – Unknown",
    "“Life is like a sandwich. No matter which way you flip it, the bread comes first.” – Unknown",
    "“My favorite exercise is a cross between a lunge and a crunch. I call it lunch.” – Unknown",
    "“You know you're getting old when the candles cost more than the cake.” – Unknown",
    "“I put the ‘pro’ in procrastinate.” – Unknown",
    "“I’m sorry, I can’t hear you over the sound of how awesome I am.” – Unknown",
    "“I could agree with you, but then we’d both be wrong.” – Unknown",
    "“If you ever feel useless, just remember that the ‘Esc’ key exists.” – Unknown",
    "“Don't ever give up on your dreams. Keep sleeping.” – Unknown",
    "“I don't need a hairstylist, my pillow gives me a new hairstyle every morning.” – Unknown",
    "“I’m like a cloud. When I disappear, it’s a beautiful day.” – Unknown",
    "“I would lose weight, but I hate losing.” – Unknown",
    "“My diet plan: Make all my friends cupcakes. The cupcakes will be too cute to eat. This diet is working great.” – Unknown",
    "“I have a lot of growing up to do. I realized that the other day inside my fort.” – Unknown",
    "“I wonder what my dog named me.” – Unknown",
    "“I’m not late. I’m just on duck time.” – Unknown",
    "“Today I am going to be as productive as a sloth on a lazy day.” – Unknown",
    "“I asked the librarian if the library had any books on self-help. She said they were all checked out.” – Unknown",
    "“If you think nothing is impossible, try slamming a revolving door.” – Unknown",
    "“I don’t need therapy. I just need to scroll through memes for a while.” – Unknown",
    "“I’m not crazy, my reality is just different from yours.” – Unknown",
    "“I don’t make mistakes. I make ‘creative decisions’.” – Unknown",
    "“Procrastination is the art of keeping up with yesterday.” – Unknown",
    "“If Monday had a face, I would punch it.” – Unknown",

    # Duck-Themed Quotes for Extra Fun:
    "“I’m not a regular duck, I’m a cool duck.” – Unknown",
    "“Quack me up, I’m hilarious.” – Your Duckie Bot",
    "“What did the duck say to the duckling? ‘Stop following me around, I need some space!’” – Unknown",
    "“The early bird might get the worm, but the duck gets the bread crumbs.” – Unknown",
    "“Quack, quack, here comes the snack.” – Your Duckie Bot"
]

async def post_random_quote():
    while True:
        # Choose a random quote
        quote = random.choice(quotes)

        channel = bot.get_channel(GENERAL_CHAT_CHANNEL_ID)

        if channel:
            if isinstance(channel, TextChannel):
                await channel.send(quote)
            else:
                print("Channel is not a text channel - cannot send message.")
        else:
            print("No 'general' channel found.")

        # Wait for a random amount of time (e.g., between 30 minutes to 2 hours)
        wait_time = random.randint(7200, 21600)  # Random time between 2 hours (7200 sec) and 6 hours (21600 sec)
        await asyncio.sleep(wait_time)


# -------------------
# check brithdays
# -------------------
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
    channel = bot.get_channel(GENERAL_CHAT_CHANNEL_ID)

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
                    print("Channel is not a text channel - cannot send message.")
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
