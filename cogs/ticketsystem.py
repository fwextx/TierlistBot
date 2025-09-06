import discord
import discord.ui
from discord.ui import View, Button, Select
from discord.ext import commands
from discord import app_commands
from db.ticket_db import init_db, get_ticket_roles, add_ticket_role, remove_ticket_role
from db.suggestion_db import init_db, get_suggestion_roles, add_suggestion_role, remove_suggestion_role

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
        init_db()    

    @app_commands.command(name="set_ticket_channel", description="Set a channel for your ticket system")         #embed to be sent in tickets channel for people to create a ticket
    async def set_ticket_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.user.guild_permissions.administrator:
            embed_no_permissions = discord.Embed(                                                                #embed if you dont have the minimum permissions
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command (Administrator)",
                colour=0xFF0000
            )   
            await interaction.response.send_message(embed=embed_no_permissions, ephemeral=True)
            return

        embedwork = discord.Embed(                                                                               #embed if channel sent
            title="`✅` Ticket Channel Sent",
            description=f"You have successfully sent the Ticket message to <#{channel.id}>.",
            colour=0x00FF00
        )            
        await interaction.response.send_message(embed=embedwork, ephemeral=True)
            
        embedchannel = discord.Embed(
            title="`🎫` Create a Ticket",                                                                        #the embed message for the ticket channel
            description="To create a ticket tap the `📩` button.",
            colour=0x00b0f4
        )
        embedchannel.set_footer(
            text=f"{interaction.guild.name} - Ticket System [BETA]",
            icon_url=interaction.guild.icon.url
        )
        await channel.send(embed=embedchannel, view=self.TicketButton(self))

    @app_commands.command(name="set_ticket_support_roles", description="Add a support role for tickets")        #command to set ticket support roles
    async def set_ticket_support_roles(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command (Manage Roles).",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)
            return
        
        ticket_roles = get_ticket_roles()
        
        if role.id in ticket_roles:
            remove_ticket_role(role.id)
            action = "removed from"
        else:
            add_ticket_role(role.id)
            action = "added to"
        
        embedticket = discord.Embed(
            title="`✅` Allowed Roles Updated",
            description=f"{role.mention} has been **{action}** the **Ticket Support** role(s) list.",
            colour=0x00FF00
        )
        embedticket.set_footer(
            text=interaction.guild.name
        )
        await interaction.response.send_message(embed=embedticket, ephemeral=True)

    @app_commands.command(name="set_suggestion_support_roles", description="Add a support role for tickets")            #command to set suggestion support roles
    async def set_suggestion_support_roles(self, interaction: discord.Interaction, role: discord.Role):
        if not interaction.user.guild_permissions.manage_roles:
            embedfail = discord.Embed(
                title="`❓` No Permissions",
                description="You do not have the permissions required for this command (Manage Roles)",
                colour=0xFF0000
            )
            await interaction.response.send_message(embed=embedfail, ephemeral=True)
            return
        
        suggestion_roles = get_suggestion_roles()
        
        if role.id in suggestion_roles:
            remove_suggestion_role(role.id)
            action = "removed from"
        else:
            add_suggestion_role(role.id)
            action = "added to"
        
        embedsuggestion = discord.Embed(
            title="`✅` Allowed Roles Updated",
            description=f"{role.mention} has been **{action}** the **Ticket Suggestion Team** role(s) list.",
            colour=0x00FF00
        )
        embedsuggestion.set_footer(
            text=interaction.guild.name
        )
        await interaction.response.send_message(embed=embedsuggestion, ephemeral=True)

    async def ticket_callback(self, interaction: discord.Interaction):                                             #list of tickets
        guild = interaction.guild
        ticket_roles = get_ticket_roles()
        ticketrole = [guild.get_role(role_id) for role_id in ticket_roles if guild.get_role(role_id)]
        suggestion_roles = get_suggestion_roles()
        suggestionrole = [guild.get_role(role_id) for role_id in suggestion_roles if guild.get_role(role_id)]

        overwrites_rest_of_tickets =  {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True)
        }

        overwrites_suggestions = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True)
        }

        for role in ticketrole:                                                                           #the role you're editing
            overwrites_rest_of_tickets[role] = discord.PermissionOverwrite(view_channel=True)             #view rest of tickets channel
            overwrites_suggestions[role] = discord.PermissionOverwrite(view_channel=True)                 #view suggestion channel's too

        for role in suggestionrole:
            overwrites_suggestions[role] = discord.PermissionOverwrite(view_channel=True)
        
        select = Select(options=[
            discord.SelectOption(label="Help", value="01", emoji="📚", description="Need Support? Select this option and our Support Team will help you right away!"),
            discord.SelectOption(label="Suggestions", value="02", emoji="❓", description="Got Suggestions? Select this option and our Support Team will think!"),
            discord.SelectOption(label="Bug Reports", value="03", emoji="🤖", description="Got a Bug Report? Select this option and our Support Team will handle it immediately!"),
            discord.SelectOption(label="Other...", value="04", emoji="⚠️", description="Need help in Other Stuff? Select this option and our Support Team will help you right away!")
        ])

        async def my_callback(interaction: discord.Interaction):

            category = discord.utils.get(guild.categories, name="Tickets")       #can set it for roles too by changing "categories" to "roles"
            if category is None:
                category = await guild.create_category("Tickets")

            embedcallsupport = discord.Embed(                                      #embed if system failed
                title="`📛` Request Failed",
                description="Please contact @ftayyeh. if this issue appears.",
                colour=0xFF0000
            )

            if select.values[0] == "01":
                channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites_rest_of_tickets)

                action = "Help"

                embed_tickets = discord.Embed(                                       #embed which will reply in the tickets channel once you create a ticket
                    title="`🎫` Ticket Created",
                    description=f"You have successfully created a ticket at <#{channel.id}>",
                    colour=0x00b0f4
                )
                embed_tickets.set_footer(
                    text=interaction.guild.name
                )

                embedinticket = discord.Embed(                                        #embed to be put in tickets
                    title=f"`🎫` This is a {action} ticket.",
                    description=f"Support will here shortly.\nTo close this ticket, please press the `🔒` button.",
                    colour=0x00b0f4
                )

                await interaction.response.send_message(embed=embed_tickets, ephemeral=True)
                await channel.send(f"{interaction.user.mention}", embed=embedinticket, view=self.CloseTicketButton(self))

            elif select.values[0] == "02":
                channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites_suggestions)

                action = "Suggestion"

                embed_tickets = discord.Embed(                                       #embed which will reply in the tickets channel once you create a ticket
                    title="`🎫` Ticket Created",
                    description=f"You have successfully created a ticket at <#{channel.id}>",
                    colour=0x00b0f4
                )
                embed_tickets.set_footer(
                    text=interaction.guild.name
                )

                embedinticket = discord.Embed(                                        #embed to be put in tickets
                    title=f"`🎫` This is a {action} ticket.",
                    description=f"Support will here shortly.\nTo close this ticket, please press the `🔒` button.",
                    colour=0x00b0f4
                )

                await interaction.response.send_message(embed=embed_tickets, ephemeral=True)
                await channel.send(f"{interaction.user.mention}", embed=embedinticket, view=self.CloseTicketButton(self))

            elif select.values[0] == "03":
                channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites_rest_of_tickets)

                action = "Bug Reports"

                embed_tickets = discord.Embed(                                       #embed which will reply in the tickets channel once you create a ticket
                    title="`🎫` Ticket Created",
                    description=f"You have successfully created a ticket at <#{channel.id}>",
                    colour=0x00b0f4
                )
                embed_tickets.set_footer(
                    text=interaction.guild.name
                )

                embedinticket = discord.Embed(                                        #embed to be put in tickets
                    title=f"`🎫` This is a {action} ticket.",
                    description=f"Support will here shortly.\nTo close this ticket, please press the `🔒` button.",
                    colour=0x00b0f4
                )

                await interaction.response.send_message(embed=embed_tickets, ephemeral=True)
                await channel.send(f"{interaction.user.mention}", embed=embedinticket, view=self.CloseTicketButton(self))

            elif select.values[0] == "04":
                channel = await guild.create_text_channel(f"{interaction.user.name}-ticket", category=category, overwrites=overwrites_rest_of_tickets)

                action = "Other..."

                embed_tickets = discord.Embed(                                       #embed which will reply in the tickets channel once you create a ticket
                    title="`🎫` Ticket Created",
                    description=f"You have successfully created a ticket at <#{channel.id}>",
                    colour=0x00b0f4
                )
                embed_tickets.set_footer(
                    text=interaction.guild.name
                )

                embedinticket = discord.Embed(                                        #embed to be put in tickets
                    title=f"`🎫` This is a {action} ticket.",
                    description=f"Support will here shortly.\nTo close this ticket, please press the `🔒` button.",
                    colour=0x00b0f4
                )

                await interaction.response.send_message(embed=embed_tickets, ephemeral=True)
                await channel.send(f"{interaction.user.mention}", embed=embedinticket, view=self.CloseTicketButton(self))

            else:
                await interaction.response.send_message(embed=embedcallsupport, ephemeral=True)

        select.callback = my_callback
        view = View(timeout=None)
        view.add_item(select)
        await interaction.response.send_message("Choose an option below:",view=view, ephemeral=True)

    class TicketButton(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @discord.ui.button(label="", emoji="📩", style=discord.ButtonStyle.primary, custom_id="make_ticket")
        async def make_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await self.cog.ticket_callback(interaction)

    class CloseTicketButton(discord.ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @discord.ui.button(label="", emoji="🔒", style=discord.ButtonStyle.primary, custom_id="delete_ticket")
        async def delete_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.channel.delete()


async def setup(bot):
    await bot.add_cog(Ticket(bot))