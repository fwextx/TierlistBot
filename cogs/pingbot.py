import discord
from discord.ext import commands
from discord import app_commands

class PingBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")

    @app_commands.command(name="ping", description="Show's you the bot's ping (MS)")
    async def botping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"```{self.bot.user.name}'s Ping: {round(self.bot.latency * 1000)}MS```")

async def setup(bot):
    await bot.add_cog(PingBot(bot))


