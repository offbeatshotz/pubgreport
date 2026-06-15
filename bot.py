import discord
from discord import app_commands
from discord.ext import commands
import os
from urllib.parse import quote
from dotenv import load_dotenv

# --- Environment and Path Setup ---
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    """Event that fires when the bot is online and ready."""
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# --- Slash Commands ---

@bot.tree.command(name="player_report", description="Generates a pubg.report link for a player.")
@app_commands.describe(player_name="The in-game name of the PUBG player.")
async def player_report(interaction: discord.Interaction, player_name: str):
    """Generates and posts a link to a player's pubg.report page."""
    
    # URL-encode the player name to handle special characters
    encoded_player_name = quote(player_name)
    
    # Construct the URL
    report_url = f"https://pubg.report/players/{encoded_player_name}"
    
    # Create a simple embed message
    embed = discord.Embed(
        title=f"PUBG Report for {player_name}",
        description=f"Click the link below to see the latest reports for **{player_name}**.",
        color=discord.Color.red(),
        url=report_url
    )
    embed.add_field(name="Report Link", value=report_url)
    embed.set_thumbnail(url="https://pubg.report/assets/pubg-report-logo-b6032488.png") # pubg.report logo
    
    await interaction.response.send_message(embed=embed)


# --- Run the bot --- #
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("Error: DISCORD_TOKEN not found in .env file.")
