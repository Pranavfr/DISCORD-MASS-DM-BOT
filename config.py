import discord
from discord.ext import commands
from bot import DISCORD_TOKEN  # Import DISCORD_TOKEN from bot.py
import asyncio
from discord import app_commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Enable message content intent

class MyBot(commands.Bot):
    async def setup_hook(self):
        # Sync commands with Discord
        await self.tree.sync()

bot = MyBot(command_prefix='!', intents=intents)

# List to store channel IDs where the bot should not auto-respond
excluded_channels = []

# List to store channel IDs where the bot should add the ✅ reaction
scrims_channels = []

# Flag to control message sending
stop_sending = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def send_message(member: discord.Member, message: str):
    if not member.bot:
        try:
            await member.send(message)
            print(f"Sent message to {member.name}")
        except discord.Forbidden:
            print(f"Could not send message to {member.name}")

@bot.command()
@commands.has_permissions(administrator=True)
async def mass_dm(ctx, *, message: str):
    global stop_sending
    stop_sending = False
    members = ctx.guild.members
    total_members = len(members)
    sent_count = 0

    progress_message = await ctx.send(f"Invite sent to {sent_count}/{total_members} users.")
    print(f"Invite sent to {sent_count}/{total_members} users.")  # Log to terminal

    for member in members:
        if stop_sending:
            break
        await send_message(member, message)
        sent_count += 1
        await progress_message.edit(content=f"Invite sent to {sent_count}/{total_members} users.")
        print(f"Invite sent to {sent_count}/{total_members} users. Sent to: {member.name}")  # Log to terminal
        await asyncio.sleep(1)  # Add a delay to avoid rate limits

    await ctx.send(f"Mass DM completed. Invite sent to {sent_count}/{total_members} users.")
    print(f"Mass DM completed. Invite sent to {sent_count}/{total_members} users.")  # Log to terminal

@bot.command()
@commands.has_permissions(administrator=True)
async def stop_sending_msgs(ctx):
    global stop_sending
    stop_sending = True
    await ctx.send("Message sending will be stopped.")

@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def _kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"Kicked {member.name} for reason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not kick {member.name}")

@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def _ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"Banned {member.name} for reason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message(f"Could not ban {member.name}")

@bot.tree.command(name="timeout", description="Timeout a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def _timeout(interaction: discord.Interaction, member: discord.Member, duration: str):
    time_dict = {'m': 60, 'h': 3600, 'd': 86400}
    amount = int(duration[:-1])
    unit = duration[-1]
    if unit in time_dict:
        seconds = amount * time_dict[unit]
        try:
            await member.timeout_for(seconds=seconds)
            await interaction.response.send_message(f"Timed out {member.name} for {duration}")
        except discord.Forbidden:
            await interaction.response.send_message(f"Could not timeout {member.name}")
    else:
        await interaction.response.send_message("Invalid duration format. Use m (minutes), h (hours), or d (days).")

@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(administrator=True)
async def _warn(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    if not member.bot:
        try:
            await member.send(f"You have been warned for: {reason}")
            await interaction.response.send_message(f"Warned {member.name} for reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message(f"Could not warn {member.name}")
    else:
        await interaction.response.send_message("Cannot warn a bot.")

# Run the bot with your token
bot.run(DISCORD_TOKEN)
