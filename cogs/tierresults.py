import discord
from discord.ext import commands
from discord import app_commands
from db.role_db import init_db, add_role, remove_role, get_allowed_roles

REGIONS = [
    app_commands.Choice(name="North America", value="NA"),
    app_commands.Choice(name="Europe", value="EU"),
    app_commands.Choice(name="Asia", value="AS")
]

GAMEMODES = [
    app_commands.Choice(name="Sword", value="Sword"),
    app_commands.Choice(name="Mace", value="Mace"),
    app_commands.Choice(name="Axe", value="Axe"),
    app_commands.Choice(name="UHC", value="UHC"),
    app_commands.Choice(name="NethPot", value="Nethpot"),
    app_commands.Choice(name="SMP", value="SMP"),
    app_commands.Choice(name="CPvP", value="CPvP"),
    app_commands.Choice(name="DSMP", value="Diamond SMP"),
    app_commands.Choice(name="DiaPot", value="DiaPot")
]

class tierresults(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")

    @app_commands.command(name="tier_player", description="Giving a user his tier results")
    @app_commands.describe(region="Select the player's region.")
    @app_commands.choices(region=REGIONS)
    @app_commands.describe(gamemode="Select the gamemode the player has tested on.")
    @app_commands.choices(gamemode=GAMEMODES)
    async def tier_player(self, interaction: discord.Interaction,channel: discord.TextChannel, user: discord.Member, tester: discord.Member, region: app_commands.Choice[str], username: str, test_score: str, previous_rank: discord.Role, earned_rank: discord.Role, gamemode: app_commands.Choice[str]):

        user_role_ids = [role.id for role in interaction.user.roles]
        if any(role_id in get_allowed_roles() for role_id in user_role_ids):

            channel_obj = channel
            if channel_obj:

                embed = discord.Embed(
                    colour=0x00b0f4
                )

                embed.set_author(
                    name=f"{user}'s Tier Results 🏆",
                    icon_url=user.display_avatar.url
                )

                embed.add_field(
                    name="Tester:",
                    value=tester.mention,
                    inline=False
                )
                embed.add_field(
                    name="Region:",
                    value=region.value,
                    inline=False
                )
                embed.add_field(
                    name="Username:",
                    value=username,
                    inline=False
                )      
                embed.add_field(
                    name="Previous Rank:",
                    value=previous_rank,
                    inline=False
                )
                embed.add_field(
                    name="Rank Earned:",
                    value=earned_rank,
                    inline=False
                )
                embed.add_field(
                    name="Score",
                    value=test_score,
                    inline=False
                )
                embed.add_field(
                    name="Gamemode:",
                    value=gamemode.value,
                    inline=False
                )
                embed.set_thumbnail(
                    url=f"https://render.crafty.gg/3d/bust/{username}"
                )

                if previous_rank in user.roles:
                    await user.remove_roles(previous_rank)
                if earned_rank not in user.roles:
                    await user.add_roles(earned_rank)

                embedwork = discord.Embed(
                    title="`✅` Player Tiered",
                    description="You have tiered a user, Nice!",
                    colour=0x00FF00
                )
                embedwork.set_footer(
                    text=interaction.guild.name
                )
                await interaction.response.send_message(embed=embedwork, ephemeral=True)
                message = await channel_obj.send(content=f"{user.mention}", embed=embed) 
                await message.add_reaction("👑")
                await message.add_reaction("🔥")
                await message.add_reaction("😭") 
                await message.add_reaction("🥳")
                await message.add_reaction("😱")
                await message.add_reaction("💀")

            else:
                embednochannel = discord.Embed(
                    title="`📛` Channel Not Found",
                    description="I couldn't find the specified channel.",
                    colour=0xFF0000
                )
                await interaction.response.send_message(embed=embednochannel, ephemeral=True)
        else:
            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)


async def setup(bot):
    await bot.add_cog(tierresults(bot))