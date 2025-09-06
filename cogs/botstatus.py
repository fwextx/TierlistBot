import discord
from discord.ext import commands, tasks
from itertools import cycle

class botstatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_statuses = cycle(["Clans PVP", "Minecraft"])
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
        self.change_bot_status.start()
    
    @tasks.loop(seconds=60)
    async def change_bot_status(self):
        await self.bot.change_presence(
            activity=discord.Game(next(self.bot_statuses)),
            status=discord.Status.do_not_disturb
        )

async def setup(bot):
    await bot.add_cog(botstatus(bot))