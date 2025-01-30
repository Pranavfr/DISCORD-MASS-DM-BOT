import discord
from discord.ext import commands
from bot import DISCORD_TOKEN  # Import DISCORD_TOKEN from bot.py

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Flag to control message sending
stop_sending = False

@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.command()
@commands.has_permissions(administrator=True)
async def send_all(ctx, *, message: str):
    global stop_sending
    stop_sending = False  # Reset the flag when the command is called

    for member in ctx.guild.members:
        if stop_sending:
            await ctx.send("Message sending has been stopped.")
            return

        if not member.bot:
            try:
                await member.send(message)
                print(f"Sent message to {member.name}")
            except discord.Forbidden:
                print(f"Could not send message to {member.name}")

    await ctx.send("Message sent to all members.")

@bot.command()
@commands.has_permissions(administrator=True)
async def stop_sending_msgs(ctx):
    global stop_sending
    stop_sending = True
    await ctx.send("Message sending will be stopped.")

bot.run(DISCORD_TOKEN)