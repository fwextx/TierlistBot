import discord
from discord.ext import commands
from discord import app_commands
from db.region_db import init_db, add_region_role, remove_region_role, get_region_role

class waitlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
        init_db()

    @app_commands.command(name="set_waitlist_channel", description="create a waitlist entry")
    async def set_waitlist_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        view = self.WaitlistView(self)
        
        if not interaction.user.guild_permissions.administrator:

            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)
            return

        channel_obj = channel
        if channel_obj:

            embed = discord.Embed(
                title="`🗒️` Evaluation Testing Waitlist",
                description="After applying, you will be added to a waitlist channel.\nYou will be notified as soon as a tester is available for your region.\nIf you are HT3 or higher, you will instead be placed into a high-priority ticket.",
                color=0x00b0f4
            )
            embed.add_field(
                name="",
                value="The region you select should match where you are located.",
                inline=False
            )
            embed.add_field(
                name="",
                value="The username you provide must be the exact account you will be testing on.",
                inline=False
            )

            embedwork = discord.Embed(
                title="`✅` Waitlist Channel Sent",
                description=f"You have successfully sent the Waitlist message to <#{channel.id}>",
                colour=0x00FF00
            )

            await interaction.response.send_message(embed=embedwork, ephemeral=True)
            await channel_obj.send(embed=embed, view=view)

    class WaitlistView(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog
    
        @discord.ui.button(label="Enter Waitlist", style=discord.ButtonStyle.primary)
        async def enter_waitlist_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            
            guild = interaction.guild
            member = interaction.user

            region_roles = get_region_role()

            for region_role_id, give_role_id in region_roles.items():
                region_role = guild.get_role(region_role_id)
                give_role = guild.get_role(give_role_id)

                if region_role and region_role in member.roles:
                    if give_role:
                        if give_role not in member.roles:
                            try:
                                await member.add_roles(give_role)
                                embedentered = discord.Embed(
                                    title="`✅` Entered Waitlist",
                                    description="You have successfully entered the Waitlist.",
                                    colour=0x00FF00
                                )
                                await interaction.response.send_message(embed=embedentered, ephemeral=True)
                                return
                            except discord.Forbidden:
                                embednopermission = discord.Embed(
                                    title="`❓` No Permissions",
                                    description="You do not have the permissions required for this command",
                                    colour=0xFF0000
                                )
                                await interaction.response.send_message(embed=embednopermission, ephemeral=True)
                                return
                        else:
                            embedalready = discord.Embed(
                                title="`ℹ️` Already on Waitlist",
                                description="You are already on the Waitlist.",
                                colour=0xFFFF00
                            )
                            await interaction.response.send_message(embed=embedalready, ephemeral=True)
                            return

            embednovalidroles = discord.Embed(
                title="`❓` No Roles",
                description="There were no roles found to give.",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embednovalidroles, ephemeral=True)
    
        
    @app_commands.command(name="set_region_role", description="Add a waitlist role so people can enter the waitlist")
    async def set_region_role(self, interaction: discord.Interaction, region_role: discord.Role, give_role: discord.Role):

        if not interaction.user.guild_permissions.administrator:
            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)
            return
        
        allowed_roles = get_region_role()

        if region_role.id in allowed_roles:
            remove_region_role(region_role.id)
            action = "removed"
            action2 = ""
        else:
            add_region_role(region_role.id, give_role.id)
            action = "added"
            action2 = f", and give them **role** {give_role.mention}"

        embedaddregionrole = discord.Embed(
            title="`✅`Updated Region Roles",
            description=f"{action} **proxy** {region_role.mention}{action2}.",
            colour=0x00FF00
        )
        embedaddregionrole.set_footer(
            text=interaction.guild.name
        )

        await interaction.response.send_message(embed=embedaddregionrole, ephemeral=True)
        
async def setup(bot):
    await bot.add_cog(waitlist(bot))