import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

SHOP_CHANNEL_ID = 0  # Mets ton salon ici après

# ========= READY =========

@bot.event
async def on_ready():
    print(f"Connecté : {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sync : {len(synced)}")
    except Exception as e:
        print(e)

# ========= RANK =========

@bot.tree.command(name="rank", description="Voir le rank RL")
@app_commands.describe(player="Pseudo Epic")
async def rank(interaction: discord.Interaction, player: str):

    url = f"https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/{player}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        await interaction.response.send_message("Joueur introuvable.")
        return

    data = r.json()

    segments = data["data"]["segments"]

    msg = ""

    for s in segments:
        if s["type"] == "playlist":
            name = s["metadata"]["name"]
            tier = s["stats"]["tier"]["metadata"]["name"]
            division = s["stats"]["division"]["metadata"]["name"]

            msg += f"🏆 {name}\n{tier} {division}\n\n"

    embed = discord.Embed(
        title=f"Rank de {player}",
        description=msg,
        color=0x00b0f4
    )

    await interaction.response.send_message(embed=embed)

# ========= SHOP =========

@bot.tree.command(name="shop", description="Boutique RL")
async def shop(interaction: discord.Interaction):

    url = "https://rl.insider.gg/fr/pc"

    embed = discord.Embed(
        title="Boutique Rocket League",
        description=f"Voir la boutique ici : {url}",
        color=0xff9900
    )

    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)