#!/usr/bin/env python3
import discord
import random
import os
import time
import asyncio
import json
from mutagen.mp3 import MP3
from datetime import date
from datetime import datetime
import datetime
from sympy import *
from discord.ext import commands
import requests

TOKEN = (DISCORD_TOKEN)
help_command = commands.DefaultHelpCommand(no_category = 'Commands')
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or('#'), help_command = help_command, intents=intents)

hoerbuecher_data = {}
current_hoerbuch = ""
hoerbuch_start_time = 0
hoerbuch_end_time = 0

queue_list = []
curr_song = ""
pause_song = ""

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Game('Discord'))

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    blacklist = ["#pferdegeruch!", "Hurensohn", "Wichser"]
    msg_content = message.content.lower()
    if any(word in msg_content for word in blacklist):
        await message.delete()
    await bot.process_commands(message)

@bot.command(name='hello', help = 'Respondse Hello.')
async def hello(ctx, msg):
    await ctx.send('Hello')
    print("{}: Hello".format(ctx.message.author.name))

@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int=1, number_of_sides: int=6):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))
    print("{}: Hat gewürfelt. Ergebnis: ".format(ctx.message.author.name) + ', '.join(dice))

@bot.command(name='join', help='Bot joint in Channel')
async def join(ctx):
    voice_client = ctx.message.guild.voice_client
    if not ctx.message.author.voice:
        await ctx.send("{} ist in keinem Channel".format(ctx.message.author.name))
        return
    else:
        try:
            await voice_client.disconnect()
            channel = ctx.message.author.voice.channel
        except:
            channel = ctx.message.author.voice.channel
    await channel.connect()
    await ctx.send("joined {} to voice channel".format(ctx.message.author.name))
    print("{}: join channel".format(ctx.message.author.name))

@bot.command(name='leave', help='Bot verlässt Channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    voice_channel = ctx.message.guild.voice_client
    try:
        voice_channel.stop()
    except:
        print(" ")
    try:
        await voice_client.disconnect()
        await ctx.send("leave voice channel")
    except:
        await ctx.send("The bot is not connected to a voice channel.")
    print("{}: Leave channel".format(ctx.message.author.name))

@bot.command(name='play', help='Bot plays song', aliases=["p"])
async def play(ctx, *, url):
    await play_song(ctx, url, "play")

async def play_song(ctx, url, type):
    voice_client = ctx.voice_client
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing() and type == "check_queue":
        return
    elif not voice_client.is_playing() and type == "check_queue":
        queue_list.pop(0)
    if voice_client.is_playing():
        voice_channel.stop()

    async with ctx.typing():
        file = await YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source=file), 0.7))

    await ctx.send('**Jetzt läuft:** {}'.format(getTitle()))
    print("{}: Play song    ".format(ctx.message.author.name) + "Title: {}".format(getTitle()))

    await after_play(getTitle(), getFilename())
    #await leaving(ctx)

@bot.command(name='queue', help='queue song [alpha]', aliases=['q'])
async def queue(ctx, *, url):
    queue_list.append([ctx, url, datetime.datetime.now()])

async def play_queue():
    if queue_list != []:
        print(queue_list)
        ctx = queue_list[0][0]
        url = queue_list[0][1]
        await play_song(ctx, url, "check_queue")
        return True
    return False

@bot.command(name='list', help='list queue [debug]')
async def list_queue(ctx):
    await ctx.send(queue_list)

@bot.command(name='next', help='next song [alpha]', aliases=['n'])
async def next(ctx):
    if queue_list != []:
        voice_channel = ctx.message.guild.voice_client
        await ctx.send("**next**")
        voice_channel.stop()

        ctx = queue_list[0][0]
        url = queue_list[0][1]
        queue_list.pop(0)
        await play_song(ctx, url, "next")
    else:
        await ctx.send('**no song in queue**')

async def leaving(ctx):
    print(ctx.message.author.voice.channel.members)

async def status(title: str="discord", activity: str="game"):
    if activity == "game":
        status = discord.Activity(type=discord.ActivityType.playing, name=title)
    elif activity == "listen":
        status = discord.Activity(type=discord.ActivityType.listening, name=title)
    await bot.change_presence(activity=status)

async def after_play(title, filename):
    global curr_song
    curr_song = title
    await status(title=title, activity="listen")
    await asyncio.sleep(getDuration())

    if curr_song == title and pause_song == "":
        await status(title="Discord", activity="game")
        curr_song = ""
        await clear_dir(filename)
        print("finished {}".format(title))
        if queue_list != []:
            await play_queue()
    elif pause_song != title:
        await clear_dir(filename)

async def clear_dir(title):
    try:
        os.remove(title)
    except:
    	return

@bot.command(name="stop", help="Stop playing song.")
async def stop(ctx):
    voice_channel = ctx.message.guild.voice_client
    await ctx.send("**stop**")
    voice_channel.stop()
    os.remove(getFilename())
    queue_list.clear()
    await bot.change_presence(activity=bot.guilds[0].get_member(bot.user.id).activity)
    await status(title="Discord", activity="game")
    print("{}: Stop".format(ctx.message.author.name))

@bot.command(name="pause", help="pause playing song")
async def pause(ctx):
    global curr_song, pause_song
    voice_client = ctx.message.guild.voice_client
    await ctx.send("**pause**")
    voice_client.pause()
    pause_song = curr_song
    curr_song = ""
    await status(title="Discord", activity="game")
    print("{}: Pause".format(ctx.message.author.name))

@bot.command(name="resume", help="resume song")
async def resume(ctx):
    global curr_song, pause_song
    curr_song = pause_song
    pause_song = ""
    voice_client = ctx.message.guild.voice_client
    await ctx.send("**resume**")
    voice_client.resume()
    print("{}: Resume".format(ctx.message.author.name))

@bot.command(name="echo", help="echo")
async def echo(ctx, * , msg):
    await ctx.send(msg)
    print("{}: Echo     ".format(ctx.message.author.name) + "echo: ".join(msg))

@bot.command(name="fuck", help="Fuck you.")
async def fuck(ctx, * , msg):
    if msg == "you":
        await ctx.send('**Fuck you.**', tts=true)

    elif msg == "off":
        await ctx.send('Okay.')
    else:
        await ctx.send("Fuck " + msg)
    print("{}: Fuck ".format(ctx.message.author.name) + "".join(msg))

@bot.command(name="dm", help="Nachrichten per DM senden. Bsp.: ;dm @Nutzer @Nutzer1 eine Nachricht")
async def dm(ctx, users: commands.Greedy[discord.User], *, message):
    for user in users:
        await user.send("from {} : ".format(ctx.message.author.name) + message)
        print('{} send: "'.format(ctx.message.author.name) + message +'" to {}'.format(user))

@bot.command(name="getPrice", help="showing current stock market price.", aliases=["getP"])
async def getPrice(ctx, comp, number: int = 1):
    price = yf.Ticker(comp)
    price = price.info['regularMarketPrice']
    out = "Current price of "
    curr = "$"
    if "eur" in comp:
        curr = "€"
    if number != 1:
        out = "Total value of {} shares ".format(number)
    print("{}: getPrice     ".format(ctx.message.author.name) + "from: {}".format(comp) + "={}".format(price*number))
    await ctx.send(out + comp + ": {}".format(round(number *price,4)) + curr)

@bot.command(name="DOGE", help="show current DOGE Price.", aliases=["doge"])
async def doge(ctx, currency: str = "eur", number: float = 1):
    out = "Current price:"
    if currency == "usd" :
        price = yf.Ticker("DOGE-USD")
        doge = price.info['regularMarketPrice']
        curr = "$"
    else:
        price = yf.Ticker("DOGE-EUR")
        doge = price.info['regularMarketPrice']
        curr = "€"

    print("{}: DOGE         ".format(ctx.message.author.name) + "price/value: {}".format(number*doge))
    await ctx.send(out + " {}".format(round(number *doge,4)) + curr)

@bot.command(name="ping", help="Shows latency")
async def ping(ctx):
    await ctx.send("Mein Ping ist {} ms ".format(round(bot.latency * 1000)))
    print("{}: Ping         ".format(ctx.message.author.name) + "Ping: {}".format(round(bot.latency * 1000)))

async def say(msg):
    channel = bot.get_channel(756947903515197510)
    await channel.send(msg)

@bot.command(name = "twitch", help = "check if a stream is on" )
async def twitch(ctx, user):
    url= 'https://www.twitch.tv/' +user
    contents = requests.get(url).content.decode('utf-8')
    if 'isLiveBroadcast' in contents:
        await ctx.send(f"{user} ist live: \n{url}")
    else:
        await ctx.send(f"{user} scheint nicht live zu sein")

@bot.command(name = "pferdegeruch!")
async def pferd(ctx):
    voice_client = ctx.voice_client
    #await ctx.message.delete()
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing():
        voice_channel.stop()
    voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source="sounds/Du-stinkst-nach-Pferd.mp3"), 2))
    await ctx.message.delete()

@bot.command(name="log")
async def log(ctx, *, args: str = ""):
    dir = "/home/quigon/logwatch/"
    file = "{}{}.log".format(dir, date.today())

    service = "all"
    detail = "high"
    range = "today"

    if "help" in args:
        await ctx.send("Befehl um Serverbericht zu bekommen mit logwatch\nBsp.:\n #log \n#log -range yesterday/month/24h -detail high/low -service sshd\n")
        return

    if str(ctx.message.author) == "McFly#6766":
        if args != "":
            args = args.split("-")

            args.pop(0)
            argslst = []
            for arg in args:
                elem = arg.split(" ")

                if len(elem) > 2:
                    elem.pop()
                argslst.append(elem)
            print(argslst)
            for arg in argslst:
                if len(arg) != 2:
                    await ctx.send("fehlendes Argument oder zu viele bei '{}'".format(arg[0]))
                    continue
                if arg[0] == "service":
                    service = arg[1]
                if arg[0] == "detail":
                    detail = arg[1]
                if arg[0] == "range":
                    range = arg[1]
        if range == "month":
            range = "between today and last month"
        if range == "today+yesterday":
            range = "between today and yesterday"
        if range == "24h":
            range = "between now and 24 hours ago"

        os.system("logwatch --service {} --detail {} --range '{}' --filename ~/logwatch/$(date +%F).log".format(service, detail, range))
        try:
            await ctx.send(file=discord.File(r'{}'.format(file)))
        except Exception:
            await ctx.send("Es wurde kein Bericht angefertigt, vllt. ist ein Parameter falsch?")

        """
        #print log, but too large
        file_read = open(file, "r")
        logtxt = str(file_read.read().strip())
        file_read.close()
        print(logtxt)
        await ctx.send("{}".format(logtxt))
        """

    elif ctx.message.author != "McFly#6766":
        await ctx.send("@{} Keine Berechtigung!".format(ctx.message.author.name))

@bot.command(name="WerBinIch")
async def WerBinIch(ctx):
   await ctx.send(f'Du bist {ctx.message.author}')

@bot.command(name="solve", aliases=["löse"], help = "#solve/löse help/hilfe")
async def solve(ctx,*,inp: str):
    if inp == "help" or inp == "hilfe":
        await ctx.send("Einfach Gleichung eingeben \nBeachte: \nExponenten bitte mit ** angeben, Bsp.: 2² == 2 ** 2 \nBitte 2 * x statt 2x \nWurzel: sqrt() \nDas Programm kann nur mit einer Variable umgehen \nVariablen sind einzelne Buchstaben \nfür bessere, visuelle Darstellung Jupyter benutzen \n ")
        return

    alph = "xyzabcdfghijklmnopqrstuvw"
    for i in range(len(alph)-1):
        locals()[alph[i]] = symbols("{}".format(alph[i]))

    i = str(inp)

    if inp.__contains__("="):
        inp = inp.split("=")
        l = eval(inp[0])
        r = eval(inp[1])
        g = Eq(l,r)
        e = solveset(g)
    else:
        inp = inp.split("=")
        e = eval(inp[0])

    preview(e, viewer="file", filename="temp.png")

    with open("temp.png", "rb") as fh:
        f = discord.File(fh, filename="temp.png")

    await ctx.send(N(e))
    await ctx.send(file=f)

#hinzufügen der abgespielten Zeit, wenn komplett gehört
@bot.command(name = "Kassette_einlegen", help = "Kasette (ein Hörbuch) wird in den Kassettenspieler eingelegt")
async def Kassette_einlegen(ctx, buch: str = ""):
    hoerbuecher_data = await read_from_hoerbuch()

    voice_client = ctx.voice_client
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing():
        voice_channel.stop()

    await setGlobalParam(buch)
    hoerbuecher_data["Hörbücher"]["{}".format(buch)][1] = "0"
    await write_to_hoerbuch(hoerbuecher_data)

    async with ctx.typing():
        file = "Hörbücher/{}.mp3".format(buch)
        voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source=file), 0.5))
	#das wird immer ausgeführt, auch wenn nicht vollständig abgespielt,also unbrauchbar
        #hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1] = hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][0]
        #await write_to_hoerbuch(hoerbuecher_data)

    await ctx.send('Kassette **{}** wurde eingelegt und wird nun gespielt'.format(buch))
    print("{}: Hörbuch      ".format(ctx.message.author.name) + "Title: {}".format(buch))

    duration = hoerbuecher_data["Hörbücher"]["{}".format(buch)][2]
    await hoerbuch_status(buch, duration)


#done
@bot.command(name = "Kassette_pause")
async def Kassette_pause(ctx):
    hoerbuecher_data = await read_from_hoerbuch()

    hoerbuch_end_time = datetime.datetime.now()
    gespielte_zeit_gesamt = hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1]
    if gespielte_zeit_gesamt == "0":
        gespielte_zeit = hoerbuch_end_time - hoerbuch_start_time
    else:

        gespielte_zeit_gesamt = datetime.datetime.strptime(gespielte_zeit_gesamt, "%H:%M:%S.%f")
        gespielte_zeit_gesamt_delta = datetime.timedelta(hours=gespielte_zeit_gesamt.hour, minutes=gespielte_zeit_gesamt.minute, seconds=gespielte_zeit_gesamt.second, microseconds=gespielte_zeit_gesamt.microsecond)
        gespielte_zeit = hoerbuch_end_time - hoerbuch_start_time + gespielte_zeit_gesamt
        gespielte_zeit = datetime.timedelta(hours=gespielte_zeit.hour, minutes=gespielte_zeit.minute, seconds=gespielte_zeit.second, microseconds=gespielte_zeit.microsecond)

    hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1] = str(gespielte_zeit)

    voice_channel = ctx.message.guild.voice_client
    await ctx.send("Abspielen der Kassette wird pausiert und kann später fortgesetzt werden.")
    voice_channel.stop()

    await bot.change_presence(activity=bot.guilds[0].get_member(bot.user.id).activity)
    await bot.change_presence(activity=discord.Game('Discord'))
    print("{}: Pause Hörbuch".format(ctx.message.author.name))

    await write_to_hoerbuch(hoerbuecher_data)

#hinzufügen der abgespielten Zeit, wenn komplett gehört
@bot.command(name = "Kassette_fortsetzen")
async def Kassette_fortsetzen(ctx, buch: str = current_hoerbuch):
    hoerbuecher_data = await read_from_hoerbuch()

    global current_hoerbuch
    if current_hoerbuch == "":
        current_hoerbuch = buch

    gespielte_zeit = hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1]

    voice_client = ctx.voice_client
    if voice_client == None:
        await ctx.message.author.voice.channel.connect()
        voice_client = ctx.voice_client

    server = ctx.message.guild
    voice_channel = server.voice_client

    if voice_client.is_playing():
        voice_channel.stop()

    await setGlobalParam(buch)

    async with ctx.typing():
        file = "Hörbücher/{}.mp3".format(buch)
        #timestamp = datetime.datetime.strptime(gespielte_zeit, "%H:%M:%S.%f")
        #print(timestamp)
        voice_channel.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio( source=file, before_options="-ss 0{}".format(gespielte_zeit)), 0.5))
	#das wird immer ausgeführt, auch wenn nicht vollständig abgespielt,also unbrauchbar
	#hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1] = hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][0]
        #await write_to_hoerbuch(hoerbuecher_data)

    await ctx.send('Kassette **{}** wird nun bei {} fortgesetzt.'.format(buch, gespielte_zeit))
    print("{}: Hörbuch      ".format(ctx.message.author.name) + "Title: {}".format(buch))

    duration = hoerbuecher_data["Hörbücher"]["{}".format(buch)][2]
    await hoerbuch_status(buch, duration)

#done
@bot.command(name = "Kassette_stop")
async def Kassette_stop(ctx):
    hoerbuecher_data = await read_from_hoerbuch()

    voice_channel = ctx.message.guild.voice_client
    await ctx.send("Abspielen der Kassette wird gestoppt und kann nicht mehr fortgesetzt werden.")
    voice_channel.stop()
    hoerbuecher_data["Hörbücher"]["{}".format(current_hoerbuch)][1] = "0"
    await bot.change_presence(activity=bot.guilds[0].get_member(bot.user.id).activity)
    await bot.change_presence(activity=discord.Game('Discord'))
    print("{}: Stop Hörbuch".format(ctx.message.author.name))

    await write_to_hoerbuch(hoerbuecher_data)

#pausenzeiten
@bot.command(name = "Kassette_liste")
async def Kassette_liste(ctx, inp: str = ""):
    hoerbuecher_data = await read_from_hoerbuch()
    buch_liste = []

    for buch in hoerbuecher_data["Hörbücher"].keys():
        dauer = hoerbuecher_data["Hörbücher"]["{}".format(buch)][0]
        zeit = hoerbuecher_data["Hörbücher"]["{}".format(buch)][1]
        buch_liste.append("{} ({}) abgespielte Zeit :{}".format(buch, dauer, zeit))

    await ctx.send("Alle verfügbaren Kassetten:\n{}".format(buch_liste))

#done
@bot.command(name = "Kassette_laden", aliases = ["Kassetten_laden"])
async def Kassette_laden(ctx):
    dir = "Hörbücher"
    buecher = os.listdir(dir)
    loaded = 0

    hoerbuecher_data = await read_from_hoerbuch()

    for buch in buecher:
        buch = buch.replace(".mp3", "")
        if buch in hoerbuecher_data["Hörbücher"]:
            continue
        elif buch != "Hörbücher.json":
            hoerbuecher_data["Hörbücher"]["{}".format(buch)] = []
            #dauer finden und ins dict schreiben
            audio = MP3("Hörbücher/{}.mp3".format(buch))
            audio_info = audio.info
            length_in_secs = int(audio_info.length)
            hours, mins, seconds = await convert(length_in_secs)
            dauer = "{}:{}:{}.0".format(hours, mins, seconds)
            hoerbuecher_data["Hörbücher"]["{}".format(buch)].append(dauer)
            hoerbuecher_data["Hörbücher"]["{}".format(buch)].append("0")
            hoerbuecher_data["Hörbücher"]["{}".format(buch)].append(audio_info.length)
            await ctx.send("Folgende Kassette wurde hinzugefügt:\n{}".format(buch))
            loaded += 1
        if loaded == 0:
            await ctx.send("Keine neuen Kassetten wurden geladen.")
        await write_to_hoerbuch(hoerbuecher_data)

#done
@bot.command(name = "Kassette_json", aliases = ["Kassetten_json", "Kassetten.json"])
async def Kassette_json(ctx):
    hoerbuecher_data = await read_from_hoerbuch()
    await ctx.send("Hörbücher.json:\n{}".format(hoerbuecher_data))

async def write_to_hoerbuch(hoerbuecher_data):
    open("Hörbücher/Hörbücher.json", "w").close()
    with open('Hörbücher/Hörbücher.json', 'a',encoding="utf-8") as file:
        json.dump(hoerbuecher_data, file, indent=4)

async def read_from_hoerbuch():
    f = open("Hörbücher/Hörbücher.json")
    hoerbuecher_data = json.load(f)
    return hoerbuecher_data

async def setGlobalParam(buch):
    global hoerbuch_start_time
    hoerbuch_start_time = datetime.datetime.now()
    global current_hoerbuch
    current_hoerbuch = buch

#done
async def hoerbuch_status(buch, duration):
    #global start
    #start = time.time()
    hoerbuecher_data = await read_from_hoerbuch()
    gespielte_zeit = hoerbuecher_data["Hörbücher"]["{}".format(buch)][1]
    if gespielte_zeit != "0":
        gespielte_zeit = datetime.datetime.strptime(gespielte_zeit, "%H:%M:%S.%f")
        gespielte_zeit = datetime.timedelta(hours=gespielte_zeit.hour, minutes=gespielte_zeit.minute, seconds=gespielte_zeit.second, microseconds=gespielte_zeit.microsecond)
        gespielte_zeit = gespielte_zeit.total_seconds()
        duration = duration - gespielte_zeit

    status = discord.Activity(type=discord.ActivityType.listening, name= buch)
    await bot.change_presence(activity=status)
    await asyncio.sleep(duration)
    await bot.change_presence(activity=discord.Game('Discord'))

async def convert(seconds):
    hours = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    seconds %= 60
    return hours, mins, seconds

@bot.command(name = "w2g", help = "W2G Link erstellen", aliases = ["link","Link","W2G","w2g_link"])
async def wtwog(ctx, *, url: str = ""):
    import w2g
    link = w2g.room_create(W2G_API_KEY, url)
    await ctx.send("{}".format(link))

@bot.command(name = "mcWhitelist")
async def mcWhitelist(ctx, name: str = ""):
    pass

@bot.command(name="mcLog")
async def mcLog(ctx, file: str = "latest"):
    pass

@bot.command(name="kill" , help="kill program")
async def kill(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send("shutting down the MegaBot")
    print("{}: Kill".format(ctx.message.author.name))
    try:
        await voice_client.disconnect()
        await bot.close()
        os._exit(0)
    except:
        await bot.close()
        os._exit(0)

bot.run(TOKEN)
