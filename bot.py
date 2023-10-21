import discord
import interactions
import os
import json
import dotenv
import datetime

from interactions.ext.tasks import IntervalTrigger, create_task

from swear_detector import nword_counter, load_definitions, insert_json_db, get_json_db
from config import *
from embed import CustomEmbed
from word_detector import *
from misc import *
from time_trigger import DateTimeTrigger
from twitter import *

from discord.ext import commands

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = interactions.Client(token=TOKEN, intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT)

WAR = [
    #"227685510519324672",
    "1102563005704712263"
]

global_config = None

@bot.event
async def on_ready():
    print("Ready!")

    # Dump all the guilds the bot is in
    if not os.path.exists("guilds.json"):
        guilds = {}
        for guild in bot.guilds:
            guilds[int(guild.id)] = {"name" : guild.name, "tip_channel" : None}
        
        with open("guilds.json", "w") as f:
            json.dump(guilds, f)

    load_definitions()
    init_generic_word_db()
    init_tips()

    # Load the global config
    guilds = [str(guild.id) for guild in bot.guilds]
    init_config(guilds)

@bot.event
async def on_guild_join(guild):
    guilds = {}
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    
    guilds[int(guild.id)] = guild.name

    with open("guilds.json", "w") as f:
        json.dump(guilds, f)

    print("Added guild")

@bot.event
async def on_guild_remove(guild):
    guilds = {}
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    
    guilds.pop(int(guild.id))

    with open("guilds.json", "w") as f:
        json.dump(guilds, f)

    print("Removed guild")

@bot.event(name="on_message_create")
async def on_message(message):
    if message.author.bot:
        return
    
    content = message.content
    ctx = await message.get_channel()

    # Process the message
    nwords = nword_counter(content)
    total = nwords[0] + nwords[1]

    # if is_alerts(str(message.guild_id)): return
    # The N word alerts are always on
    if total > 0:
        await ctx.send(f"@everyone: **{message.author.mention}** has said the n-word **{total}** {'time' if total == 1 else 'times'}, **{nwords[1]}** of which {'was' if nwords[1] == 1 else 'were'} a hard r!")
        insert_json_db(str(message.author.mention), nwords[0], nwords[1])



@bot.event(name="on_message_create")
async def on_message_custom(message):
    if message.author.bot:
        return
    
    content = message.content.lower()
    ctx = await message.get_channel()
    guild = await message.get_guild()

    # Process the message
    words = generic_word_counter(guild.id, content, str(message.author.mention))

    # Assemble the message to alert members
    if is_alerts(str(message.guild_id)): return
    if len(words) > 0:
        msg = f"**{message.author.mention}** said the following words: \n"
        for word in words:
            msg += f"`{word} x {words[word]}`\n "

        await ctx.send(msg)

@bot.event(name="on_message_create")
async def kys(message):
    if message.author.bot:
        return
    
    content = message.content.lower()
    ctx = await message.get_channel()
    guild = await message.get_guild()

    if any(word in content for word in ['slay']):
        await message.create_reaction("😐")

@bot.event(name="on_message_create")
async def twitter_replacer(message):
    if message.author.bot:
        return
    
    content = message.content.lower()
    ctx = await message.get_channel()
    guild = await message.get_guild()

    if is_twitter_link(message.content.lower()):
        # replace twitter or x with vxtwitter
        await message.reply(replace_twitter_link(message.content.lower()))


@bot.event(name="on_message_create")
async def the_fine_bros(message):
    # return
    if str(message.author.id) in WAR: # The Fine Bros react to harrison
        await message.create_reaction("👎")
        # await message.reply("Bender tosser wanker")
    
    if str(message.author.id) == "526983628408881179":
        return
        # await message.reply("not slay")
        # await message.create_reaction("🤡")
        # await message.create_reaction(":yay:")

@bot.command(
    name="nword",
    description="Get the n-word count of a user",
    options=[
        interactions.Option(
            name="user", 
            description="The user to get the n-word count of", 
            type=3, 
            required=True
        ),
    ],
)
async def nword_count(ctx, user: str):
    data = get_json_db(user)
    if data is None:
        await ctx.send("User not found")
        return

    embed = CustomEmbed(
        title="N Word Count",
        description=f"How many times has {user} said the n-word?",
        color=0x00FF00,
        fields=[
            {
                "name": "N-Words",
                "value": data['nwords'],
                "inline": False
            },
            {
                "name": "Hard r's",
                "value": data['hard_rs'],
                "inline": True
            },
            {
                "name": "Summary",
                "value": f"{user} has said the n-word {data['nwords']} {'time' if data['nwords'] == 1 else 'times'} of which {data['hard_rs']} {'was' if data['hard_rs'] == 1 else 'were'} {'a hard r' if data['hard_rs'] == 1 else 'hard rs'}",
                "inline": False
            }
        ]
    )

    await ctx.send(embeds=[embed])

@bot.command(
    name="register",
    description="Register a word to be monitored on this server",
    options=[
        interactions.Option(
            name="word",
            description="The word to register",
            type=3,
            required=True
        )
    ]
)
async def register_word(ctx, word: str):
    # Register the word here
    server = ctx.guild_id

    if server is None:
        await ctx.send("This command can only be used in a server")
        return
    
    if word is None:
        await ctx.send("You need to specify a word")
        return
    
    if word in get_generic_words(server=str(server)):
        await ctx.send("This word is already registered")
        return
    
    res = register_generic_word(str(server), word.lower())
    if res:
        await ctx.send(f"Successfully registered `{word}`")
    else:
        await ctx.send("Word probably already registered")

@bot.command(
    name="unregister",
    description="Unregister a word to be monitored on this server",
    options=[
        interactions.Option(
            name="word",
            description="The word to unregister",
            type=3,
            required=True
        )
    ]
)
async def unregister(ctx, word: str):
    server = ctx.guild_id

    if server is None:
        await ctx.send("This command can only be used in a server")
        return
    
    if word is None:
        await ctx.send("You need to specify a word")
        return
    
    if word not in get_generic_words(server=str(server)):
        await ctx.send("This word is not registered")
        return
    
    res = unregister_generic_word(str(server), word.lower())
    if res:
        await ctx.send(f"Successfully unregistered `{word}`")
    else:
        await ctx.send("Word probably not registered")

@bot.command(
    name="summary",
    description="Get a summary of a single word registered on this server",
    options=[
        interactions.Option(
            name="word",
            description="The word to get a summary of",
            type=3,
            required=True
        )
    ]
)
async def summarize(ctx, word: str):
    server = ctx.guild_id

    if server is None:
        await ctx.send("This command can only be used in a server")
        return
    
    if word is None:
        await ctx.send("You need to specify a word")
        return
    
    if word not in get_generic_words(server=str(server)):
        await ctx.send("This word is not registered")
        return
    
    data = get_generic_words(server=str(server))
    if word not in data:
        await ctx.send("This word is not registered")
        return
    
    data = data[word]['total']
    
    embed = CustomEmbed(
        title="Word Summary",
        description=f"Summary of the word `{word}`",
        color=0x00FF00,
        fields=[
            {
                "name": "Count",
                "value": data,
                "inline": False
            }
        ]
    )

    await ctx.send(embeds=[embed])

@bot.command(
    name="summary_all",
    description="Get a summary of all words registered on this server"
)
async def summary_all(ctx):
    # Attach the entire generic_db.json file
    guild = str(ctx.guild_id)
    with open("generic_db.json", "r") as f:
        db = json.loads(f.read())
        text = ""

        # Sort the words by total count
        words = sorted(db[guild].items(), key=lambda x: x[1]['total'], reverse=True)
        
        for word in words:
            text += f"`{word[0]}` : {word[1]['total']} {'time' if word[1]['total'] == 1 else 'times'}\n"

        await ctx.send(text)

@bot.command(
    name="leaderboard",
    description="Get the top 5 users for a word on this server",
    options=[
        interactions.Option(
            name="word",
            description="The word to get the leaderboard of",
            type=3,
            required=True
        )
    ]
)
async def leaderboard(ctx, word: str):
    server = ctx.guild_id
    if server is None:
        await ctx.send("This command can only be used in a server")
        return
    
    if word is None:
        await ctx.send("You need to specify a word")
        return
    
    if word not in get_generic_words(server=str(server)):
        await ctx.send("This word is not registered")
        return
    
    data = get_top_users(server=str(server), word=word)
    if data is None:
        await ctx.send("No data found")
        return
    
    ordinals = ["1st", "2nd", "3rd", "4th", "5th"]
    embed = CustomEmbed(
        title="Leaderboard",
        description=f"Top 5 users for the word `{word}`",
        color=0xFF00FF,
        # data[0][0] is the user's name, data[0][1] is the user's count
        fields=[
            {
                "name": ordinals[i],
                "value": f"{entry[0]} : {entry[1]} {'time' if entry[1] == 1 else 'times'}",
                "inline": False
            }
            for i, entry in enumerate(data[:5])
        ]
    )

    await ctx.send(embeds=[embed])

@bot.command(
    name="tip",
    description="Get a random tip"
)
async def tip(ctx):
    await ctx.send(random_tip())

@bot.command(
    name="subscribe",
    description="Subscribe this channel to receive tips"
)
async def subscribe(ctx):
    guild = str(ctx.guild_id)
    channel = str(ctx.channel_id)

    await ctx.send(str(type(ctx.channel_id)))

    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    
    if guild not in guilds:
        await ctx.send("This guild is not registered")
        return
    
    guilds[guild]['tip_channel'] = channel

    with open("guilds.json", "w") as f:
        json.dump(guilds, f)
    
    await ctx.send("Successfully subscribed to tips")

@bot.command(
    name="toggle_alerts",
    description="Toggle alerts on this server"
)
async def toggle_alerts(ctx):
    server = str(ctx.guild_id)
    config = get_config(server)
    set_alerts(server, not config['alerts'])
    await ctx.send(f"Alerts are now {'on' if config['alerts'] else 'off'}")

# This part runs tip messages.
@create_task(DateTimeTrigger(datetime.datetime.now() + datetime.timedelta(seconds=5)))
async def tip_task():
    with open("guilds.json", "r") as f:
        guilds = json.load(f)
    
    for guild in guilds:
        if guilds[guild]['tip_channel'] is not None:
            channel_id = interactions.api.models.misc.Snowflake(guilds[guild]['tip_channel'])
            channel = interactions.api.models.channel.Channel(id=channel_id, type=0)
            await channel.send(random_tip())

# tip_task.start() broken

@bot.event(
    name="guild_audit_log_entry_create"
)
async def on_guild_audit_log_entry_create(entry):
    print(entry)



bot.start()