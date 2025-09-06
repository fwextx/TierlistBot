import discord
from datetime import datetime, timezone
from discord.ext import commands, tasks
from discord import app_commands
from discord.errors import Forbidden
from db.role_db import init_db, add_role, remove_role, get_allowed_roles

CHOICES = [
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove")
]


class QueueView(discord.ui.View):
    def __init__(self, cog, channel_id):
        super().__init__(timeout=None)
        self.cog = cog
        self.channel_id = channel_id

    @discord.ui.button(label="Join Queue", style=discord.ButtonStyle.primary, custom_id="join_button")
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue_data = self.cog.channel_queues.get(self.channel_id)
        if not queue_data:
            return
        queue, testers, queue_message = queue_data["queue"], queue_data["testers"], queue_data["queue_message"]

        user = interaction.user
        if user.id in queue:
            embed = discord.Embed(
                title="⚠️ Already in Queue",
                description="You're already in this queue!",
                colour=0xFF0000
            )
            embed.set_footer(text=interaction.guild.name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if len(queue) >= 5:
            embed = discord.Embed(
                title="⛔ Queue Full",
                description="The queue is full (max 5 users)",
                colour=0xFF0000
            )
            embed.set_footer(text=interaction.guild.name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        queue.append(user.id)
        if len(queue) == 1:
            try:
                first_user = self.cog.bot.get_user(queue[0])
                if first_user:
                    embed_dm = discord.Embed(
                        title="🧪 First in Queue",
                        description=f"<@{queue[0]}> You're first in queue, please create a ticket!",
                        colour=0x00b0f4
                    )
                    await first_user.send(embed=embed_dm)
            except Forbidden:
                print(f"Could not DM user {queue[0]} (forbidden).")

        if queue_message:
            new_embed = self.cog.generate_embed(channel_id=self.channel_id)
            await queue_message.edit(embed=new_embed)

        embed = discord.Embed(
            title="✅ Queue Joined",
            description="You have successfully joined the queue.",
            colour=0x00FF00
        )
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Leave Queue", style=discord.ButtonStyle.gray, custom_id="leave_button")
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        queue_data = self.cog.channel_queues.get(self.channel_id)
        if not queue_data:
            return
        queue, testers, queue_message = queue_data["queue"], queue_data["testers"], queue_data["queue_message"]

        user = interaction.user
        if user.id not in queue:
            embed = discord.Embed(
                title="⚠️ Not in Queue",
                description="You're not in this queue.",
                colour=0xFF0000
            )
            embed.set_footer(text=interaction.guild.name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        queue.remove(user.id)
        if queue:
            try:
                first_user = self.cog.bot.get_user(queue[0])
                if first_user:
                    embed_dm = discord.Embed(
                        title="🧪 First in Queue",
                        description=f"<@{queue[0]}> You're first in queue, please create a ticket!",
                        colour=0x00b0f4
                    )
                    await first_user.send(embed=embed_dm)
            except Forbidden:
                print(f"Could not DM user {queue[0]} (forbidden).")

        if queue_message:
            new_embed = self.cog.generate_embed(channel_id=self.channel_id)
            await queue_message.edit(embed=new_embed)

        embed = discord.Embed(
            title="✅ Left Queue",
            description="You have successfully left the queue.",
            colour=0x00FF00
        )
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_queues = {}  # channel_id: {queue, testers, queue_message, view, guild_id}
        init_db()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Cog ready")
        print("------------------------")

    def generate_embed(self, channel_id):
        data = self.channel_queues.get(channel_id)
        if not data:
            return discord.Embed(title="Queue not initialized.")
        queue, testers = data["queue"], data["testers"]

        embed = discord.Embed(
            title="Tester(s) Are Available!",
            description=" 🧪 The queue updates every 20 seconds.",
            colour=0x00b0f4
        )

        guild = self.bot.get_guild(data.get("guild_id"))
        if guild:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)

        queue_list = "\n".join([f"{i + 1}. <@{uid}>" for i, uid in enumerate(queue)]) or "*Queue is currently empty.*"
        embed.add_field(name="__Queue:__", value=queue_list, inline=False)

        if testers:
            testers_list = "\n".join([f"{i + 1}. {tester.mention}" for i, tester in enumerate(testers)])
        else:
            testers_list = "No testers assigned."
        embed.add_field(name="Testers:", value=testers_list, inline=False)

        embed.set_image(
            url="https://media.discordapp.net/attachments/1352769804498501685/1354794805779234946/standard_1.gif")
        return embed

    async def start_queue(self, interaction: discord.Interaction, channel: discord.TextChannel, testers: list):
        channel_id = channel.id
        if channel_id not in self.channel_queues:
            self.channel_queues[channel_id] = {
                "queue": [],
                "testers": testers,
                "queue_message": None,
                "view": None,
                "guild_id": interaction.guild.id
            }

        view = QueueView(self, channel_id)
        self.channel_queues[channel_id]["view"] = view

        embed = self.generate_embed(channel_id)
        queue_msg = await channel.send("# ||@here||", embed=embed, view=view)
        self.channel_queues[channel_id]["queue_message"] = queue_msg

        if not self.update_queue_embed.is_running():
            self.update_queue_embed.start()

    @app_commands.command(name="test", description="Start a small test for 5 players in their queued gamemodes")
    async def test(self, interaction: discord.Interaction, channel: discord.TextChannel, tester_n1: discord.Member,
                   tester_n2: discord.Member = None, tester_n3: discord.Member = None, tester_n4: discord.Member = None,
                   tester_n5: discord.Member = None):
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in get_allowed_roles() for role_id in user_role_ids):
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        testers = [tester_n1, tester_n2, tester_n3, tester_n4, tester_n5]
        testers = [t for t in testers if t]
        await self.start_queue(interaction, channel, testers)

        embed = discord.Embed(title="✅ Queue Launched", description="Your queue has been launched.", colour=0x00FF00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="leave", description="Leave a queue you're in")
    async def leave(self, interaction: discord.Interaction):
        for channel_id, data in self.channel_queues.items():
            if interaction.user.id in data["queue"]:
                data["queue"].remove(interaction.user.id)
                if data["queue"]:
                    try:
                        first_user = self.bot.get_user(data["queue"][0])
                        if first_user:
                            embed_dm = discord.Embed(
                                title="🧪 First in Queue",
                                description=f"<@{data['queue'][0]}> You're first in queue, please create a ticket!",
                                colour=0x00b0f4
                            )
                            await first_user.send(embed=embed_dm)
                    except Forbidden:
                        print(f"Could not DM user {data['queue'][0]} (forbidden).")
                if data["queue_message"]:
                    new_embed = self.generate_embed(channel_id)
                    await data["queue_message"].edit(embed=new_embed)

                embed = discord.Embed(title="✅ Left Queue", description="You have successfully left the queue.",
                                      colour=0x00FF00)
                embed.set_footer(text=interaction.guild.name)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        embed = discord.Embed(title="⚠️ Not in Queue", description="You're not in a queue.", colour=0xFF0000)
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="freeze_queue", description="Disable the queue buttons so people can stop joining")
    async def freeze_queue(self, interaction: discord.Interaction, channel: discord.TextChannel):
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in get_allowed_roles() for role_id in user_role_ids):
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data = self.channel_queues.get(channel.id)
        if not data or not data["queue_message"] or not data["view"]:
            embed = discord.Embed(title="⚠️ Queue Not Found", description="No queue is active in this channel.",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        for item in data["view"].children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await data["queue_message"].edit(view=data["view"])

        embed = discord.Embed(title="🧊 Queue Frozen",
                              description="The buttons have been frozen, the queue has been closed.", colour=0x00b0f4)
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="remove_first_in_queue", description="Remove the first person from the queue")
    async def remove_first_in_queue(self, interaction: discord.Interaction, channel: discord.TextChannel):
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in get_allowed_roles() for role_id in user_role_ids):
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data = self.channel_queues.get(channel.id)
        if not data or not data["queue"]:
            embed = discord.Embed(title="📭 Queue Empty", description="Queue is currently empty", colour=0xFFFFFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        removed_id = data["queue"].pop(0)
        if data["queue"]:
            try:
                first_user = self.bot.get_user(data["queue"][0])
                if first_user:
                    embed_dm = discord.Embed(
                        title="🧪 First in Queue",
                        description=f"<@{data['queue'][0]}> You're first in queue, please create a ticket!",
                        colour=0x00b0f4
                    )
                    await first_user.send(embed=embed_dm)
            except Forbidden:
                print(f"Could not DM user {data['queue'][0]} (forbidden).")
        if data["queue_message"]:
            new_embed = self.generate_embed(channel.id)
            await data["queue_message"].edit(embed=new_embed)

        embed = discord.Embed(title="👋 User Removed", description=f"<@{removed_id}> has been removed from the queue.",
                              colour=0x00FF00)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="manage_testers", description="Remove or add a tester to the queue")
    @app_commands.choices(action=CHOICES)
    async def manage_testers(self, interaction: discord.Interaction, action: app_commands.Choice[str],
                             member: discord.Member, channel: discord.TextChannel):
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in get_allowed_roles() for role_id in user_role_ids):
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data = self.channel_queues.get(channel.id)
        if not data:
            embed = discord.Embed(title="⚠️ Queue Not Found", description="No queue is active in this channel.",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        testers = data["testers"]
        action_value = action.value.lower()
        if action_value == "add":
            if len(testers) >= 5:
                embed = discord.Embed(title="⚠️ Testers Full", description="All 5 tester slots are already filled!",
                                      colour=0xFF0000)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            testers.append(member)
            action_done = "added as a tester"
        else:
            if member in testers:
                testers.remove(member)
                action_done = "removed from tester"
            else:
                embed = discord.Embed(title="⚠️ Not a Tester",
                                      description=f"{member.mention} is not currently a tester.", colour=0xFF0000)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if data["queue_message"]:
            new_embed = self.generate_embed(channel.id)
            await data["queue_message"].edit(embed=new_embed)

        embed = discord.Embed(title="✅ Tester Updated", description=f"{member.mention} has been {action_done}.",
                              colour=0x00FF00)
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="set_tester_role", description="Set a role for testers")
    async def set_tester_role(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        allowed_roles = get_allowed_roles()
        if role.id in allowed_roles:
            remove_role(role.id)
            action = "removed from"
        else:
            add_role(role.id)
            action = "added to"

        embed = discord.Embed(title="✅ Allowed Roles Updated",
                              description=f"{role.mention} has been {action} the testers role list.", colour=0x00FF00)
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="end_test", description="End the test/queue")
    async def end_test(self, interaction: discord.Interaction, channel: discord.TextChannel):
        user_role_ids = [role.id for role in interaction.user.roles]
        if not any(role_id in get_allowed_roles() for role_id in user_role_ids):
            embed = discord.Embed(title="❓ No Permissions",
                                  description="You do not have the permissions required for this command",
                                  colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data = self.channel_queues.get(channel.id)
        if not data:
            embed = discord.Embed(title="❓ No Queue", description="There is no queue to end.", colour=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if data["queue_message"]:
            embed = discord.Embed(
                title="No Testers Online",
                description="No testers are currently online for this region.\nYou will be pinged once a tester is available.\nGo sleep!",
                colour=0x00b0f4
            )
            embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
            date = datetime.now(timezone.utc)
            timestamp = int(date.timestamp())
            embed.add_field(name="Last testing session", value=f"<t:{timestamp}:f>")
            await data["queue_message"].edit(content="", embed=embed, view=None)

        # Stop updating this channel queue
        self.channel_queues.pop(channel.id)

        embed = discord.Embed(title="🛑 Queue Ended", description="You have ended the queue.", colour=0xFF0000)
        embed.set_footer(text=interaction.guild.name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(seconds=20)
    async def update_queue_embed(self):
        for channel_id, data in self.channel_queues.items():
            if data["queue_message"]:
                new_embed = self.generate_embed(channel_id)
                await data["queue_message"].edit(embed=new_embed)


async def setup(bot):
    await bot.add_cog(Test(bot))
