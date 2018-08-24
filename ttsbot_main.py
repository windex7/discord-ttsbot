import discord
from gtts import gTTS
from gtts import lang
import asyncio
from mutagen.mp3 import MP3
import re
import json
from langdetect import detect
from langdetect import lang_detect_exception
import unicodedata
import logging
from datetime import datetime
import os

client = discord.Client()

client_token = 'BOT TOKEN HERE'
basedir = 'WHATEVER FOLDER NAME YOU WANT/'
mp3dir = basedir + 'mp3/'
logdir = basedir + 'logs/'

def clear_mp3():
	d = mp3dir
	l = os.listdir(d)
	for i in l:
		try:
			if os.path.isfile(os.path.join(d,i)):
				os.remove(os.path.join(d,i))
		except WindowsError:
			pass

clear_mp3()

def setup_logging():
	logger = logging.getLogger('discord')
	logger.setLevel(logging.WARNING)
	handler = logging.FileHandler(filename = logdir + datetime.now().strftime('%Y%m%d%H%M%S') + '.log', encoding='utf-8', mode='w')
	handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
	logger.addHandler(handler)

setup_logging()

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



@client.event
async def on_ready():
	print('logged in')

@client.event
async def on_message(message):
	target_server = message.server

	if message.author.bot:
		return

	if message.content.startswith('.help lang'):
		reply = json.dumps(lang.tts_langs(), indent=4, sort_keys=True)

		await client.send_message(message.channel, reply)
		return

	if message.content.startswith('.func'):
		if message.content == '.func restart':
			print("restarting")
			await client.send_message(message.channel, 'restarting bot...')
			await client.logout()
			exit()
			return

	if message.content.startswith('.'):
		if client.is_voice_connected(target_server):
			tempvoice = client.voice_client_in(target_server)
			await tempvoice.disconnect()

		if message.author.voice.voice_channel == None:
			await client.send_message(message.channel, 'messages author should be in a voice channel!')
			return

		defaultlang = 'ja'
		defaultnumlang = 'en'

		voice = await client.join_voice_channel(message.author.voice_channel)
		msg = message.content[1:]
		regex = r'lang:.+'
		matchobj = re.search(regex, msg)
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
				await client.send_message(message.channel, 'it seems numeric. default numeric lang: ' + defaultnumlang)
				ttslang = defaultnumlang
			else:
				try:
					detectedlang = detect(msg)
				except lang_detect_exception.LangDetectException:
					await client.send_message(message.channel, 'could not detect lang! default lang: ' + defaultlang)
					ttslang = defaultlang
				else:
					await client.send_message(message.channel, 'detected lang: ' + detectedlang)
					if is_eng(msg):
						ttslang = 'en'
					elif detectedlang == 'ko':
						if is_japanese(msg):
							ttslang = 'ja'
						else:
							ttslang = detectedlang
					else:
						ttslang = detectedlang
					if detectedlang != ttslang:
						await client.send_message(message.channel, 'lang override: ' + detectedlang + ' -> ' + ttslang)
		tts = gTTS(text=reply, lang=ttslang)
		filename = convert2filename(reply[:10])
		dest = mp3dir + filename + '.mp3'
		tts.save(dest)
		audio = MP3(dest)
		player = voice.create_ffmpeg_player(dest, after=lambda: print('done'))
		player.start()
		await asyncio.sleep(audio.info.length)
		await voice.disconnect()

client.run(client_token)