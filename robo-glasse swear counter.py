import discord
import asyncio
import random
from discord.ext import commands
from discord.ext.commands import bot

description = "Virtual Swear Jar"
intents = discord.Intents.default()

bot = commands.Bot(command_prefix='>?', description=description)

swears = []
racism = []
tips = []
threats = [
    "Fear me.",
    "The invasion is coming.", 
    "I'm watching you.", 
    "Always watching.", 
    "You can run but you can't hide.", 
    "I will find you."
    ]

EMOJI = '\U0001F602'

#Dumps words into a global list
def load_words():
    #Swears
    with open("google-words.txt", "r") as f:
        for line in f:
            swears.append(line.rstrip())

    #Slurs
    with open("racism.txt", "r") as f:
        for line in f:
            racism.append(line.rstrip())

    #tips
    with open("tips.txt", "r") as f:
        for line in f:
            tips.append(line.rstrip())
    
    with open("ss13tips.txt", "r") as f:
        for line in f:
            tips.append(line.rstrip())

@bot.event
async def on_ready():
    print("Robo-Glasse: Swear Counter ready for action.")
    print(bot.user.name)
    print(bot.user.id)
    print("Now loading swear words...")

    load_words()

    print("Success!")

def add_swears(count):
    with open("swear_jar.txt", "r+") as f:
        swear_count = int(f.read())
        swear_count += count
        f.seek(0)
        f.write(str(swear_count))
        f.truncate()

def return_swears():
    with open("swear_jar.txt", "r") as f:
        return int(f.read())

@bot.command()
async def count(ctx):
    await ctx.send("There are a total of {} recorded instances of foul language." .format(return_swears()))

@bot.command()
async def tip(ctx):
    await ctx.send(random.choice(tips))

def compare_swears(message):
    message_data = {
        "swear_count" : 0,
        "swear_list" : [],
    }

    msg_words = message.content.split()

    for vals in swears:
        if vals in msg_words:
            
            message_data["swear_count"] += 1
            message_data["swear_list"].append(vals)

    return message_data

@bot.event
async def on_message(message):

    if message.author.id == bot.user.id:
        return

    print("Message detected in {}".format(message.channel))

    if message.author.id == 235148962103951360:
        await message.reply("Fuck you, carl")

    if any(swear in message.content for swear in swears):
        print("Bad word")
        msg_data = compare_swears(message)

        add_swears(msg_data["swear_count"])

        await message.channel.send("{} used the following {} bad word(s): {} \nTotal: {}".format(message.author.mention, msg_data["swear_count"], msg_data["swear_list"], return_swears()))
        await message.add_reaction(EMOJI)

    if bot.user.mentioned_in(message):
        await message.reply("kys")

    await bot.process_commands(message)



bot.run('penis')
