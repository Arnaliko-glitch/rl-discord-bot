import discord
from discord.ext import commands
from discord import app_commands
import requests
import os
from dotenv import load_dotenv
from threading import Thread
from flask import Flask

# ================== ENV ==================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TRACKER_API = os.getenv("TRACKER_API")

# ================== BOT ==================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================== FLASK (Render fix) ==================
app = Flask("")

@app.route("/")
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run).start()

# ================== READY ==================
@bot.event
async def on_ready():
    print(f"Connecté : {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sync : {len(synced)}")
    except Exception as e:
        print("Sync error:", e)

# ================== /RANK ==================
@bot.tree.command(name="rank", description="Voir le rank Rocket League")
@app_commands.describe(player="Pseudo Epic Games")
async def rank(interaction: discord.Interaction, player: str):

    try:
        # IMPORTANT : ACK immédiat (évite 10062)
        await interaction.response.defer(thinking=True)

        url = f"https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/platform:epic:{player}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "TRN-Api-Key": TRACKER_API
        }

        r = requests.get(url, headers=headers, timeout=6)

        print("URL:", url)
        print("STATUS:", r.status_code)
        print("TEXT:", r.text)

        if r.status_code != 200:
            await interaction.followup.send("❌ Joueur introuvable.")
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

        if not msg:
            msg = "Aucun rank trouvé."

        embed = discord.Embed(
            title=f"Rank de {player}",
            description=msg,
            color=0x00b0f4
        )

        await interaction.followup.send(embed=embed)

    except discord.errors.NotFound:
        print("Interaction expirée (ignore safe)")
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur API: {e}")

# ================== /SHOP ==================
@bot.tree.command(name="shop", description="Boutique Rocket League")
async def shop(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Shop Rocket League",
        description="https://rl.insider.gg/fr/pc",
        color=0xff9900
    )

    await interaction.response.send_message(embed=embed)

# ================== START ==================
bot.run(TOKEN)
