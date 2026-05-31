import discord
from discord import app_commands
from discord.ext import commands


def setup_commands(bot: commands.Bot):
    @bot.tree.command(name="orz", description="Say orz")
    @app_commands.describe(name="Who to orz")
    async def hello(interaction: discord.Interaction, name: str = "lookcook"):
        await interaction.response.send_message(f"orz {name}!")

