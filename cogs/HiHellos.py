import discord
from discord.ext import commands

class HiHellos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
    
    @commands.command(aliases=["hello?", "hello!", "hello.", "hello-"])
    async def hello(self, ctx):
        await ctx.send(f"Hi, {ctx.author.mention}!")
    
    @commands.command(aliases=["hi?", "hi!", "hi.", "hi-"])
    async def hi(self, ctx):
        await ctx.send(f"Hello, {ctx.author.mention}!")
    
    @commands.command(aliases=["hey?", "hey!", "hey.", "hey-"])
    async def hey(self, ctx):
        await ctx.send(f"Hey, {ctx.author.mention}!")
    
    @commands.command(aliases=["sup?", "sup!", "sup.", "sup-"])
    async def sup(self, ctx):
        await ctx.send(f"Sup, {ctx.author.mention}!")

    @commands.command(aliases=["nuke_sequence_881"])
    async def nuke(self, ctx):
        await ctx.send(f"Reverting bot, getting ready to delete all data in guild.")

    @commands.command(aliases=["cancel_nuke"])
    async def cancelnuke(self, ctx):
        await ctx.send(f"Reverting bot to normal, nuking process canceled.")
    
async def setup(bot):
    await bot.add_cog(HiHellos(bot))