import discord
from discord.ext import commands
import os
import easy_pil
import random

class welcomemsg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} Configured")
        print("------------------------")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        welcome_channel: discord.TextChannel = self.bot.get_channel(1359195744564805802)
        images = [image for image in os.listdir("./cogs/welcome_images")]
        randomized_image = random.choice(images)

        bg = easy_pil.Editor(f"./cogs/welcome_images/{randomized_image}").resize((1920, 1080))
        avatar_image = await easy_pil.load_image_async(str(member.avatar.url))
        avatar = easy_pil.Editor(avatar_image).resize((250, 250)).circle_image()

        font_big = easy_pil.Font.montserrat(size=90, variant="bold")
        font_small = easy_pil.Font.montserrat(size=60, variant="bold")

        bg.paste(avatar, (835, 340))
        bg.ellipse((835, 340), 250, 250, outline="white", stroke_width=6)

        bg.text((960, 620), f"Welcome to {member.guild.name}!", color="white", font=font_big, align="center")
        bg.text((960, 740), f"You're member #{member.guild.member_count}!", color="white", font=font_small, align="center")

        img_file = discord.File(fp=bg.image_bytes, filename=randomized_image)

        await welcome_channel.send(f"**Welcome, {member.mention}!**")
        await welcome_channel.send(file=img_file)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):        
        leave_channel: discord.TextChannel = self.bot.get_channel(1359195744564805802)
        await leave_channel.send(f"**Come back later, {member.mention}!**")

async def setup(bot):
    await bot.add_cog(welcomemsg(bot))