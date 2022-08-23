import discord
from gtts import gTTS
from gtts import lang
# import AquesTalkPy
# from AquesTalkPy import yukkuri
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
from datetime import datetime
import os

import queue

song_queue = queue.Queue()

def clear_mp3(d, targetext):
    l = os.listdir(d)
    for i in l:
        try:
            if os.path.isfile(os.path.join(d, i)):
                path = os.path.join(d, i)
                extpair = os.path.splitext(path)
                ext = extpair[1]
                if ext == targetext:
                    os.remove(os.path.join(d, i))
        except WindowsError:
            pass


def setup_logging(logdir):
    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(
        filename=logdir + datetime.now().strftime('%Y%m%d%H%M%S') + '.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def is_japanese(string):
    for ch in string:
        if ch == '\n':
            continue
        else:
            name = unicodedata.name(ch)
            if "CJK UNIFIED" in name \
                    or "HIRAGANA" in name \
                    or "KATAKANA" in name:
                return True
    return False


numreg = re.compile(r'^[\s0-9!-/:-@[-`{-~]+$')


def is_num(string):
    return numreg.match(string) is not None


alphareg = re.compile(r'^[\sa-zA-Z]+$')


def is_eng(string):
    return alphareg.match(string) is not None


halfsymbolreg = re.compile("[\r\n!-/:-@[-`{-~]")
fullsymbolreg = re.compile(u"[︰-＠]")
filenameheader = 'tts_'


def convert2filename(string):
    result = halfsymbolreg.sub("", string)
    result = fullsymbolreg.sub("", result)
    result = filenameheader + result
    return result


def process_msg(msg, defaultlang, defaultnumlang):
    regex = r'lang:.+'
    matchobj = re.search(regex, msg)
    ttslang = defaultlang
    if matchobj:
        langdic = lang.tts_langs()
        group = matchobj.group()
        reply = msg.replace(group, '')
        grouplang = group.replace('lang:', '')
        if grouplang in langdic:
            ttslang = grouplang
        else:
            ttslang = defaultlang
    else:
        reply = msg
        if is_num(msg):
            #await message.channel.send('it seems numeric. default numeric lang: ' + defaultnumlang)
            ttslang = defaultnumlang
        else:
            try:
                detectedlang = detect(msg)
            except lang_detect_exception.LangDetectException:
                #await message.channel.send('could not detect lang! default lang: ' + defaultlang)
                ttslang = defaultlang
            #else:
                #await message.channel.send('detected lang: ' + detectedlang)
            if is_eng(msg):
                ttslang = 'en'
            elif detectedlang == 'ko':
                if is_japanese(msg):
                    ttslang = 'ja'
                else:
                    ttslang = detectedlang
            else:
                ttslang = detectedlang
                #if detectedlang != ttslang:
                    #await message.channel.send('lang override: ' + detectedlang + ' -> ' + ttslang)
    
    return reply, ttslang

def process_gtts(reply, ttslang, mp3dir):
    tts = gTTS(text=reply, lang=ttslang)
    filename = convert2filename(reply[:10])
    dest = mp3dir + filename + '.mp3'
    tts.save(dest)
    return dest

def get_audioqueue():
    return song_queue

def get_nextaudio():
    q = get_audioqueue()
    return q.get()

def put_audioqueue(vc, dest):
    q = get_audioqueue()
    q.put((vc, dest))
    return

def isempty_audioqueue():
    q = get_audioqueue()
    return q.empty()

def playsound(vc, dest):
    if not vc.is_playing():
        audio = discord.FFmpegPCMAudio(source=dest)
        vc.play(audio, after=play_next)
    else:
        put_audioqueue(vc, dest)
        print('audio queued: ' + dest)

def play_next(err):
    if not isempty_audioqueue():
        nextaudio = get_nextaudio()
        vc = nextaudio[0]
        dest = nextaudio[1]
        if vc.is_playing():
            put_audioqueue(vc, dest)
            play_next(None)
        else:
            audio = discord.FFmpegPCMAudio(source=dest)
            vc.play(audio, after=play_next)

async def delmsg(message, logdir):
    content = message.content
    authorname = message.author.name
    f = open(logdir, 'a', encoding='UTF-8')
    f.write(authorname)
    f.write(' : ')
    f.write(content)
    f.write('\n')
    f.close()
    await message.delete()
    return

async def get_vc(message):
    if not message.author.voice:
        await message.channel.send('the author should be in a voice channel!')
        return -1

    channel = message.author.voice.channel
        
    vc = message.guild.voice_client

    if not vc:
        await channel.connect()
        vc = message.guild.voice_client
    
    return vc
