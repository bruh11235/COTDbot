import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from cfapi import *
from db.db import *


async def _error(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Error",
        description=f"Command error",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)


async def _identify(interaction: discord.Interaction, codeforces: str):
    user = interaction.user
    random_problem = get_random_problem()

    if random_problem is None:
        await _error(interaction)
        return

    embed = discord.Embed(
        title="Codeforces Handle Verification",
        description=f"{user.mention}, submit anything ONLY to "
                    f"the problem: {problem_url(random_problem)} within "
                    f"30 seconds."
    )

    await interaction.response.send_message(embed=embed)

    await asyncio.sleep(30)

    submissions = get_user_submission(codeforces)
    try:
        last_submission = submissions["result"][0]["problem"]

        assert last_submission["contestId"] == random_problem["contestId"]
        assert last_submission["index"] == random_problem["index"]

        update_mapping(str(interaction.user.id), codeforces)
        embed = discord.Embed(
            title="Codeforces Handle Verification",
            description=f"{user.mention} identified as user "
                        f"{codeforces}.",
            color=discord.Color.green()
        )

        await interaction.followup.send(embed=embed)
    except:
        embed = discord.Embed(
            title="Codeforces Handle Verification",
            description=f"{user.mention}, submission not "
                        f"received in time.",
            color=discord.Color.red()
        )

        await interaction.followup.send(embed=embed)


async def _get_handle(interaction: discord.Interaction, user: discord.User):
    cf_handle = get_cf_handle(str(user.id))

    if cf_handle is None:
        embed = discord.Embed(
            title="Handle Identification",
            description=f"No Codeforces handle found for user.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Handle Identification",
            description=f"User identified as {cf_handle}."
        )
        await interaction.response.send_message(embed=embed)


def setup_commands(bot: commands.Bot):
    @bot.tree.command(name="identify", description="Identify Codeforces handle")
    @app_commands.describe(codeforces="Codeforces handle")
    async def identify(interaction: discord.Interaction, codeforces: str):
        await _identify(interaction, codeforces)

    @bot.tree.command(name="get_handle",
                      description="Get user's Codeforces handle")
    @app_commands.describe(user="Discord User")
    async def get_handle(interaction: discord.Interaction, user: discord.User):
        await _get_handle(interaction, user)
