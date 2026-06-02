import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from commands import setup_commands, daily_update


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
setup_commands(bot)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced")


@daily_update.before_loop
async def before_daily_update():
    await bot.wait_until_ready()


@bot.event
async def setup_hook():
    if not daily_update.is_running():
        daily_update.start()
    await bot.tree.sync()


bot.run(TOKEN)
