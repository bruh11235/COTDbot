import asyncio
import discord
import datetime
from zoneinfo import ZoneInfo

from discord import app_commands
from discord.ext import commands, tasks

from cfapi import *
from db.db import *


NYC_TZ = ZoneInfo("America/New_York")


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

    # noinspection PyUnresolvedReferences
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
    cf_handle = get_account_info(str(user.id))

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
            description=f"User identified as {cf_handle[1]}."
        )
        await interaction.response.send_message(embed=embed)


async def _daily_update():
    now = datetime.datetime.now(NYC_TZ)
    if now.day != 1:
        reset_db_field("mpoints")
    reset_db_field("done_daily")

    random_problem = get_random_problem()
    set_problem(str(random_problem["contestId"]), random_problem["index"])


async def _get_cotd(interaction: discord.Interaction):
    contest_id, index = get_problem()
    embed = discord.Embed(
        title="Codeforces of the Day",
        description=f"Link to today's problem: "
                    f"https://codeforces.com/contest/{contest_id}/problem/{index}",
    )
    embed.add_field(name="Contest ID", value=contest_id, inline=True)
    embed.add_field(name="Index", value=index, inline=True)

    now = datetime.datetime.now(NYC_TZ)
    tomorrow = now.date() + datetime.timedelta(days=1)
    next_midnight = datetime.datetime.combine(
        tomorrow,
        datetime.time(hour=0, minute=0),
        tzinfo=NYC_TZ
    )
    embed.add_field(name="Next Reset",
                    value=f"<t:{int(next_midnight.timestamp())}:F>",
                    inline=True)

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

    @tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=NYC_TZ))
    async def daily_update():
        await _daily_update()

    @bot.tree.command(name="get_cotd", description="Get the Codeforces of the Day")
    async def get_cotd(interaction: discord.Interaction):
        await _get_cotd(interaction)
