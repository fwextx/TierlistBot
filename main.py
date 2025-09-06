import discord
import os
import asyncio
from discord.ext import commands, tasks
from itertools import cycle
from dotenv import load_dotenv
from cogs.test import QueueView

bot=commands.Bot(command_prefix="", intents=discord.Intents.all(), case_insensitive=True)

discord.utils.setup_logging()

bot.remove_command("help")

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")

@bot.event
async def on_ready():
    print("Hello world")
    print("------------------------")
    try:
        synced_commands = await bot.tree.sync()
        print(f"Synced {len(synced_commands)} commands.")
    except Exception as e:
        print("An error with syncing application commands has occured: ", e)

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

asyncio.run(main())