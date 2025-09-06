import discord
from discord.ext import commands
from discord import app_commands


class bancmds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")

    @app_commands.command(name="kick", description="kicks a user")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if interaction.user.guild_permissions.kick_members:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{member.mention} has been kicked.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You do not have the permmisions required for this command.", ephemeral=True)
    
    @app_commands.command(name="ban", description="bans a user")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if interaction.user.guild_permissions.ban_members:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"{member.mention} has been banned.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You do not have the required permissions for this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(bancmds(bot))