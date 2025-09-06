import discord
from discord.ext import commands
from discord import app_commands
from db.autorole_db import init_db, get_autorole_roles, add_autorole_role, remove_autorole_role

class autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_ids = get_autorole_roles(member.guild.id)
        roles_to_add = [member.guild.get_role(role_id) for role_id in role_ids if member.guild.get_role(role_id)]

        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add)
            except discord.Forbidden:
                print(f"Failed to assign joiner a role in {member.guild.name}")
    
    @app_commands.command(name="set_autorole_roles", description="Assign a role to be given to every new member once they join")
    async def set_autorole_roles(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command (Manage Roles).",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        autorole_roles = get_autorole_roles(guild_id)
        
        if role.id in autorole_roles:
            remove_autorole_role(guild_id, role.id)
            action = "removed from"
        else:
            add_autorole_role(guild_id, role.id)
            action = "added to"
        
        embedautorole = discord.Embed(
            title="`✅` Autorole Roles Updated",
            description=f"{role.mention} has been **{action}** the **Autorole** role(s) list.",
            colour=0x00FF00
        )
        embedautorole.set_footer(
            text=interaction.guild.name
        )

        await interaction.response.send_message(embed=embedautorole, ephemeral=True)

async def setup(bot):
    await bot.add_cog(autorole(bot))