import discord
import re
from discord.ext import tasks, commands
import datetime
import time
import asyncio

class StatUtility:
    def __init__(self, client):
        self.client = client

    async def getstat(self, kind, *args):
        if kind == 'emoji':
            StatUtility.getemojistat(args)
            return None
        else:
            return None

    async def getemojistat(self, textCh, msgHistoryLimit=10000, isGuildWide=False, isBotCount=False):
        allcustomemoji = await textCh.guild.fetch_emojis()
        emojiDict = dict()
        for ce in allcustomemoji:
            emojiDict[str(ce)] = 0
        if isGuildWide:
            guild = textCh.guild
        else:
            async for message in textCh.history(limit=msgHistoryLimit):
                if not isBotCount:
                    if message.author.bot:
                        continue
                custom_emoji = re.findall(r'<:\w*:\d*>', message.content)
                #custom_emoji = [int(e.split(':')[1].replace('>', '')) for e in custom_emoji]
                #custom_emoji = [discord.utils.get(self.client.get_emoji(), id=e) for e in custom_emoji]
                emojiset = set(custom_emoji)
                for e in emojiset:
                    if (e in emojiDict):
                        emojiDict[e] += 1
            emojiDictSorted = sorted(emojiDict.items(), key=lambda x:x[1], reverse=True)
            outputMsg = "\n"
            outputMsg2 = "\n"
            msgLength = 1
            MSGLIMITLEN = int(1900)
            for k, v in emojiDictSorted:
                if (v <= 0):
                    break
                t = k + " : " + str(v) + "\n"
                
                if (msgLength > MSGLIMITLEN):
                    #break
                    if (msgLength > 2 * MSGLIMITLEN):
                        break
                    else:
                        outputMsg2 += t
                else:
                    outputMsg += t

                msgLength += len(t)
            #print(outputMsg)
            await textCh.send(content = outputMsg)
            if (msgLength > MSGLIMITLEN):
                await textCh.send(content = outputMsg2)
                #for e in custom_emoji:
                #    await textCh.send(content = e)

    
