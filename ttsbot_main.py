import discord
from gtts import gTTS
from gtts import lang
#import AquesTalkPy
#from AquesTalkPy import yukkuri
import asyncio
from mutagen.mp3 import MP3
import wave
import contextlib
import re
import json
from langdetect import detect
from langdetect import lang_detect_exception
import unicodedata
import logging
import datetime
import os
import subprocess

import ttsutil
import yukkuriutil

client = discord.Client()

client_token = 'CLIENT_TOKEN'
mp3dir = 'mp3/'
logdir = 'logs/'
mp3fdir = os.getcwd() + r'\mp3'
yukdir = os.getcwd() + r'\wav'
msglogfilename = 'log.txt'
msglogfiledir = logdir + msglogfilename

ttsutil.clear_mp3(mp3fdir, '.mp3')
ttsutil.clear_mp3(yukdir, '.wav')
ttsutil.setup_logging(logdir)

@client.event
async def on_ready():
    global msglogfilename
    global msglogfiledir
    msglogfilename = 'msg_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.log'
    msglogfiledir = logdir + msglogfilename
    print('Logged in!')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith('.help lang'):
        reply = json.dumps(lang.tts_langs(), indent=4, sort_keys=True)
        await message.channel.send(reply)
        await ttsutil.delmsg(message, msglogfiledir)
        return

    if message.content.startswith('.f'):
        if message.content == '.f restart':
            print("restarting")
            await ttsutil.delmsg(message, msglogfiledir)
            await client.logout()
            exit()
            return
        elif message.content == '.f summon':
            state = message.author.voice
            if (not state) or (not state.channel):
                await message.channel.send('the author should be in a voice channel to summon')
                return
            channel = state.channel
            await channel.connect()
            await ttsutil.delmsg(message, msglogfiledir)
            return
        elif message.content == '.f disconnect':
            vc = message.guild.voice_client
            if not vc:
                await message.channel.send('the bot is not connected to VC')
                return
            await vc.disconnect()
            await ttsutil.delmsg(message, msglogfiledir)
            return

    if message.content.startswith('.'):
        defaultlang = 'ja'
        defaultnumlang = 'en'

        """
        if not message.author.voice:
            await message.channel.send('the author should be in a voice channel!')
            return

        channel = message.author.voice.channel
        vc = message.guild.voice_client

        if not vc:
            await channel.connect()
            vc = message.guild.voice_client
        """
        vc = await ttsutil.get_vc(message)
        if (vc == -1):
            return

        msg = message.content[1:]

        result = ttsutil.process_msg(msg, defaultlang, defaultnumlang)
        reply = result[0]
        ttslang = result[1]

        dest = ttsutil.process_gtts(reply, ttslang, mp3dir)

        #audio = discord.FFmpegPCMAudio(dest)
        #vc.play(audio)
        #ttsutil.playsound(vc, audio)
        ttsutil.playsound(vc, dest)

        await ttsutil.delmsg(message, msglogfiledir)
        return

    if message.content.startswith(','):
        vc = await ttsutil.get_vc(message)
        if (vc == -1):
            return
        
        msg = message.content[1:]
        if message.content.startswith(',,'):
            msg = message.content[2:]
        
        reply = msg
        speed = "100"
        
        regex = r'speed:.+'
        matchobj = re.search(regex, msg)
        if matchobj:
            group = matchobj.group()
            reply = msg.replace(group, '')
            groupspeed = group.replace('speed:', '')
            speed = groupspeed

        if message.content.startswith(',,'):
            reply = yukkuriutil.get_pron(reply)
        
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d%H%M%S')
        dest = yukdir + '\\' + filename + '.wav'
        yukkriexedest = yukdir + r'\yukkuri.exe'
        p = subprocess.run([yukkriexedest, reply, filename, yukdir, speed], check=True)
        if p.returncode == -1:
            print('failed to make audio file from: ' + reply)
            return
        
        #audio = discord.FFmpegPCMAudio(dest)
        #vc.play(audio)
        #ttsutil.playsound(vc, audio)
        ttsutil.playsound(vc, dest)

        await ttsutil.delmsg(message, msglogfiledir)
        return

client.run(client_token)
