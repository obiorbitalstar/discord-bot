from asyncio import sleep
from datetime import datetime
from glob import glob

from discord.flags import Intents
Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
								  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

from ..db import db


PREFIX = "+"
OWNER_IDS = [246751909199740942]
COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])



class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False

        self.cogs_ready = Ready()
        self.guild = None
        self.schedulaer = AsyncIOScheduler()
        
        db.autosave(self.schedulaer)

        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            Intents=Intents.all())

    def setup(self):
        for cog in COGS:
            print(cog)
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")
        
        print("setup complete")
        
    def run(self, version):
        self.VERSION = version
        
        print("running setup...")
        self.setup()
        
        with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()
        
        print("running bot...")
        super().run(self.TOKEN, reconnect=True)
    async def process_commands(self, message):
        ctx = await  self.get_context(message, cls= Context)
        
        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send('Am not ready to recive commands please wait')

    async def rules_reminder(self):
        await  self.standout.send("Remmber to adhere to the rules!")

    async def on_commect(self):
        print('bot connected')

    async def on_disconnect(self):
        print('bot disconnected')

    async  def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("something went wrong")

       
        await self.standout.send('An error happend')
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")
        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

        elif hasattr(exc, "original"):
            # if isinstance(exc.original, HTTPException):
			# 	await ctx.send("Unable to send message.")
            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(860468533607923712)
            self.standout = self.get_channel(860528402754306088)
            self.schedulaer.start()
            self.schedulaer.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12))
            # channel = self.get_channel(860528402754306088)
            # await channel.send('now online!')
            # embed = Embed(title="Now online", description="Leveling bot is not online", 
            #               colour = 0xFF0000, timestamp=datetime.utcnow())
            # fileds = [("Name", "Value", True),
            #             ("Another filed", "This field is next to the other one ", True),
            #             ("Thierd", "This is gonna be on its own row",False)]
            # for name, value ,inline in fileds:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="Sa'ed Al-Khateeb", icon_url = self.guild.icon_url)
            # embed.set_footer(text="This is a footer")
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            # await  channel.send(embed=embed)
            while not  self.cogs_ready.all_ready():
                await sleep(0.5)


            await self.standout.send("Now online!")
            self.ready = True

            print('bot ready')

        else:
            print("bot reconnected")

    async def on_messaage(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
