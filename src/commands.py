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
    if now.day == 1:
        reset_db_field("mpoints")
    reset_db_field("done_daily")

    random_problem = get_random_problem()
    set_problem(str(random_problem["contestId"]), random_problem["index"])


def _add_next_day_field(embed: discord.Embed):
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


async def _get_cotd(interaction: discord.Interaction):
    contest_id, index = get_problem()
    embed = discord.Embed(
        title="Codeforces of the Day",
        description=f"Link to today's problem: "
                    f"https://codeforces.com/contest/{contest_id}/problem/{index}",
    )
    embed.add_field(name="Contest ID", value=contest_id, inline=True)
    embed.add_field(name="Index", value=index, inline=True)
    _add_next_day_field(embed)

    await interaction.response.send_message(embed=embed)


async def _submit_cotd(interaction: discord.Interaction):
    account = get_account_info(str(interaction.user.id))

    if account is None:
        embed = discord.Embed(
            title="Codeforces account not found",
            description="Please link your Codeforces account using the "
                        "command `/identify`.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    if account[3] == 1:
        embed = discord.Embed(
            title="COTD already completed",
            description="Please wait for the next Codeforces of the Day.",
            color=discord.Color.red()
        )
        _add_next_day_field(embed)
        await interaction.response.send_message(embed=embed)
        return

    submissions = get_user_submission(account[1])
    try:
        last_submission = submissions["result"][0]["problem"]
        contest_id, idx = get_problem()

        assert str(last_submission["contestId"]) == contest_id
        assert last_submission["index"] == idx

        increment_score(str(interaction.user.id))
        embed = discord.Embed(
            title="Submission recieved",
            description=f"Congratulations!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except:
        embed = discord.Embed(
            title="Submission not recieved",
            description=f"Please have to correct submission "
                        f"be your lastest submission.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)


async def _admin_time_travel(interaction: discord.Interaction):
    account = get_account_info(str(interaction.user.id))
    if account is None or account[2] == 0:
        embed = discord.Embed(
            title="Permission Denied",
            description=f"User is not admin.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    await _daily_update()
    embed = discord.Embed(
        title="Welcome to the future",
        description=f"Daily problem updated!"
    )
    await interaction.response.send_message(embed=embed)


async def _leaderboard(interaction: discord.Interaction, monthly: bool):
    embed = discord.Embed(
        title=["", "Monthly "][monthly] + "Leaderboard (Shows top 25)",
    )
    lb = get_top_users(monthly=monthly)
    for user_id, score in lb:
        user = await interaction.client.fetch_user(int(user_id))
        embed.add_field(name=user.name,
                        value=f"{score} :coin:",
                        inline=False)
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

    @bot.tree.command(name="get_cotd",
                      description="Get the Codeforces of the Day")
    async def get_cotd(interaction: discord.Interaction):
        await _get_cotd(interaction)

    @bot.tree.command(name="submit_cotd",
                      description="Submit to the Codeforces of the Day")
    async def submit_cotd(interaction: discord.Interaction):
        await _submit_cotd(interaction)

    @bot.tree.command(name="admin_time_travel",
                      description="Admin only command")
    async def admin_time_travel(interaction: discord.Interaction):
        await _admin_time_travel(interaction)

    @bot.tree.command(name="leaderboard", description="Get leaderboard")
    @app_commands.describe(monthly="Monthly leaderboard")
    async def leaderboard(interaction: discord.Interaction,
                          monthly: bool = False):
        await _leaderboard(interaction, monthly)
