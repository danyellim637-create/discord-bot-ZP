import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import os
TOKEN = os.getenv("TOKEN")

# 자동 멘션할 역할 2개
ROLE_ID_1 = 1496696724679557271
ROLE_ID_2 = 1496696871912083516

CENTRAL_TZ = ZoneInfo("America/Chicago")
ATLANTIC_TZ = ZoneInfo("America/Halifax")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def format_ampm(dt: datetime) -> str:
    return dt.strftime("%I:%M %p").lstrip("0")


def format_countdown(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"


def build_message(label: str, time_str: str) -> str:
    cleaned = time_str.strip().upper().replace(" ", "")
    parsed = datetime.strptime(cleaned, "%I:%M%p")

    now_central = datetime.now(CENTRAL_TZ)

    event_central = datetime(
        year=now_central.year,
        month=now_central.month,
        day=now_central.day,
        hour=parsed.hour,
        minute=parsed.minute,
        tzinfo=CENTRAL_TZ
    )

    # 이미 지난 시간이면 다음 날로 넘김
    if event_central <= now_central:
        event_central += timedelta(days=1)

    atlantic_dt = event_central.astimezone(ATLANTIC_TZ)

    # 네가 원한 표시용 GMT-6
    fake_gmt6_dt = event_central - timedelta(hours=1)

    countdown = format_countdown(event_central - now_central)
    mentions = f"<@&{ROLE_ID_1}> <@&{ROLE_ID_2}>"

    return (
        f"{mentions}\n"
        f"{label} in {countdown}\n"
        f"{event_central.tzname()}: {format_ampm(event_central)}\n"
        f"{atlantic_dt.tzname()}: {format_ampm(atlantic_dt)}\n"
        f"GMT-6: {format_ampm(fake_gmt6_dt)}"
    )


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Sync failed: {e}")


@app_commands.command(name="s", description="Post Scrim countdown")
@app_commands.describe(time="Enter time like 7:30pm")
async def scrim(interaction: discord.Interaction, time: str):
    try:
        message = build_message("Scrim", time)
        await interaction.response.send_message(message)
    except ValueError:
        await interaction.response.send_message(
            "형식: 7:30pm 이렇게 써줘",
            ephemeral=True
        )


@app_commands.command(name="p", description="Post Premier countdown")
@app_commands.describe(time="Enter time like 7:30pm")
async def premier(interaction: discord.Interaction, time: str):
    try:
        message = build_message("Premier", time)
        await interaction.response.send_message(message)
    except ValueError:
        await interaction.response.send_message(
            "형식: 7:30pm 이렇게 써줘",
            ephemeral=True
        )


bot.tree.add_command(scrim)
bot.tree.add_command(premier)
bot.run(TOKEN)
