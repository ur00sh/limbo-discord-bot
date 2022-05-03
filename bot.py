#Author: Urosh Petrovic
#Project: Limbo discord bot
#Date: 3rd May 2022

import discord
import os
import requests
import json
import youtube_dl
from discord.ext import commands, tasks
from dotenv import load_dotenv

intents = discord.Intents().default()
intents.typing = False
intents.presences = False
client = discord.Client(intents = intents)
bot = commands.Bot(command_prefix = 'l!', intents=intents)


def get_results():
    response = requests.get("https://www.youtube.com/")
    json_data = json.loads(response.text)
    result = json_data[0]['q'] + " -" + json_data[0]['a']
    return(result)

@client.event
async def on_ready():
    print('You have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #if message.content.startswith('$hello'):
        #await message.channel.send('Hello')
    if message.content.startswith('l!s'):
        await message.channel.send('Results:')

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtosderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_adress': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
#integration of youtube api
class YTDLSource(discord.PCMVolumeTransformer):
    def _init_(self, source, *, data, volue = 0.5):
        super()._init_(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop = None, stream = False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = not stream))
        if 'entries' in data:
            #takes first result from the query
            data = data['entries'][0]
        fileName = data['title'] if stream else ytdl.prepare_filename(data)
        return fileName

#bot commmands
@bot.command(name = 'join', help = 'Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to the voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()

@bot.command(name = 'leave', help = 'Tells the bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel")

@bot.command(name = 'play', help = 'To play a song')
async def play(ctx, url):
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop = bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable = "ffmpeg", source = filename))
        await ctx.send('**Now playing:**{}'.format(filename))
    except:
        await ctx.send("The bot isn't connected to a voice channel")

@bot.command(name = 'pause', help = 'To pause a song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_channel
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name = 'resume', help = 'Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_channel.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command to play a song")

@bot.command(name = 'stop', help = 'Stops the song that is playing at the moment')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment")

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)
