import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
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

@bot.tree.command(name="player_report", description="Fetches the latest kill videos from a player's pubg.report page.")
@app_commands.describe(player_name="The in-game name of the PUBG player.")
async def player_report(interaction: discord.Interaction, player_name: str):
    """Scrapes pubg.report for videos and posts them in an embed."""
    
    await interaction.response.defer(ephemeral=False)
    
    encoded_player_name = quote(player_name)
    report_url = f"https://pubg.report/players/{encoded_player_name}"
    
    try:
        # Fetch the HTML content of the page
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(report_url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all match report items. This is a guess based on common website structures.
        # We are looking for divs that likely contain match data.
        matches = soup.find_all('div', class_=lambda c: c and 'match-report' in c) # Generic class search
        
        video_links = []
        # A set to avoid duplicate video URLs
        seen_urls = set()

        for match in matches:
            # Find all links within the match report item
            links = match.find_all('a', href=True)
            for link in links:
                href = link['href']
                # Check if the link is a likely video link and not a duplicate
                if ('youtube.com/watch' in href or 'twitch.tv/' in href) and href not in seen_urls:
                    video_links.append(href)
                    seen_urls.add(href)
            if len(video_links) >= 5: # Limit to the first 5 videos found
                break

        # Create the response embed
        embed = discord.Embed(
            title=f"PUBG Report for {player_name}",
            color=discord.Color.red(),
            url=report_url
        )

        if not video_links:
            embed.description = f"No recent kill videos found for **{player_name}** on their pubg.report page. You can check the full report via the link above."
        else:
            embed.description = f"Here are the latest kill videos found for **{player_name}**:"
            for i, video_url in enumerate(video_links):
                embed.add_field(name=f"Video {i+1}", value=video_url, inline=False)

        embed.set_thumbnail(url="https://pubg.report/assets/pubg-report-logo-b6032488.png")
        await interaction.followup.send(embed=embed)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            await interaction.followup.send(f"❌ Error: Player `{player_name}` not found on pubg.report.")
        else:
            await interaction.followup.send(f"❌ Error: Could not retrieve data from pubg.report. The site may be down or the player's profile is private. (Status: {e.response.status_code})")
    except Exception as e:
        await interaction.followup.send(f"❌ An unexpected error occurred: {e}")


# --- Run the bot --- #
if BOT_TOKEN:
    bot.run(BOT_TOKEN)
else:
    print("Error: DISCORD_TOKEN not found in .env file.")
