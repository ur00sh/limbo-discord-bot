#Author: Urosh Petrovic
#Project: Limbo discord bot
#Date: 3rd May 2022

#implementing needed libraries
import discord
import asyncio
import os
import requests
import json
import youtube_dl
import threading, queue
from dataclasses import dataclass, field
from typing import Any
from discord.ext import commands, tasks
from dotenv import load_dotenv
from async_timeout import timeout
from urllib import parse, request
import re


intents = discord.Intents().default()
intents.typing = False
intents.presences = False
client = discord.Client(intents = intents)

help_command = commands.DefaultHelpCommand(no_category = 'Commands')

bot = commands.Bot(command_prefix = 'l!', intents=intents, help_command = help_command)

help_command = commands.DefaultHelpCommand(no_category = 'Commands')


#pulling results from youtube
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

#ffmpeg formatting
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'audioformat': 'mp3',
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

#downloading audio and streaming it in a channel
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
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


#bot commmands
@bot.command(name = 'join', help = 'Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to the voice channel".format(ctx.message.author.name))
        await ctx.send("limbo joined.")
        return
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()

@bot.command(name = 'leave', help = 'Tells the bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("limbo left.")
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
        await ctx.send('**Now playing:** {}, enlisted by {}'.format(filename, ctx.message.author.name))
    except:
        await ctx.send("The bot isn't connected to a voice channel")
    


@bot.command(name = 'pause', help = 'To pause a song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
        await ctx.send('limbo paused by {}.'.format(ctx.message.author.name))
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name = 'resume', help = 'Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
        ctx.send('limbo resumed by {}.'.format(ctx.message.author.name))
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command to play a song")

@bot.command(name = 'stop', help = 'Stops the song that is playing at the moment')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
        ctx.send('limbo stopped by {}.'.format(ctx.message.author.name))
    else:
        await ctx.send("The bot is not playing anything at the moment")

@bot.command(name = 'limbo', help = 'Find out more about limbo')
async def limbo(ctx):
    text = "My name is limbo, I was built by uroosh and I'm still a work in progress. For more info on my features, please type 'l!help'"
    await ctx.send(text)

@bot.command(name = 'ping', help = 'ping')
async def ping(ctx):
    await ctx.send("pong.")

@bot.command(name = 'server', help = 'displays info about server')
async def server(ctx):
    Guild = ctx.guild

    await ctx.send(f'Server: {Guild.name}')
    await ctx.send(f'Members: {len(Guild.members)}')
    await ctx.send*(f'Created by: {Guild.owner.display_name}')

#loads .env file
load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)
