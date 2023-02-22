import discord
from discord.ext import tasks, commands
import datetime
import time
import asyncio

async def chattext(msg, ch):
    allowed_mentions = discord.AllowedMentions(everyone = True)
    await ch.send(content = msg, allowed_mentions = allowed_mentions)
    return

async def notifyeveryone(msg, ch):
    allowed_mentions = discord.AllowedMentions(everyone = True)
    await ch.send(content = msg, allowed_mentions = allowed_mentions)
    return

def gettextchannel(client, chname):
    return discord.utils.get(client.get_all_channels(), name=chname)

async def deletemessages(ch, len):
    async for message in ch.history(limit=len):
        await message.delete()
    return

class ChatUtility:
    def __init__(self, client, jsondir):
        # read jsonfile and add to schedule
        self.ch1 = discord.utils.get(client.get_all_channels(), name="神殿")
        self.ch2 = discord.utils.get(client.get_all_channels(), name="testpurpose")
        self.client = client
        #schedule.every().day.at("12:30").do(notifyeveryone, "@everyone リマインダー:幻影の神殿 昼の部", ch1)
        #schedule.every().day.at("19:30").do(notifyeveryone, "@everyone リマインダー:幻影の神殿 夜の部", ch1)
        #schedule.every().day.at("23:42").do(notifyeveryone, "test", ch2)
        return

    def addschedule(t, msg, ch):
        # write to json file
        #schedule.every().day.at(t).do(notifyeveryone(msg, ch))
        return

    @discord.ext.tasks.loop(seconds=10)
    async def loop(self):
        now = datetime.datetime.now()
        timer1_s = now.replace(hour=12, minute=30, second=0, microsecond=0)
        timer1_e = timer1_s + datetime.timedelta(seconds=10)
        if timer1_s <= now and now <= timer1_e:
            role1 = discord.utils.get(self.ch1.guild.roles, name="notify")
            await notifyeveryone("@here " + "<@&" + str(role1.id) + "> " + "リマインダー:幻影の神殿 昼の部", self.ch1)
        
        timer2_s = now.replace(hour=19, minute=30, second=0, microsecond=0)
        timer2_e = timer2_s + datetime.timedelta(seconds=10)
        if timer2_s <= now and now <= timer2_e:
            role1 = discord.utils.get(self.ch1.guild.roles, name="notify")
            await notifyeveryone("@here " + "<@&" + str(role1.id) + "> " + "リマインダー:幻影の神殿 夜の部", self.ch1)

        #timer3_s = now.replace(hour=10, minute=10, second=0, microsecond=0)
        #timer3_e = timer3_s + datetime.timedelta(seconds=10)
        #if timer3_s <= now and now <= timer3_e:
        #    role1 = discord.utils.get(self.ch1.guild.roles, name="notify")
        #    print("<@&" + str(role1.id) + "> " + "test")
            #ch3 = discord.utils.get(self.client.get_all_channels(), name="testpurpose")
        #    await notifyeveryone("<@&" + str(role1.id) + "> " + "test", self.ch1)