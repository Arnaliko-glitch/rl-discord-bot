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

# ================== INTENTS ==================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== READY ==================
@bot.event
async def on_ready():
    print(f"Connecté : {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sync : {len(synced)}")
    except Exception as e:
        print(e)

# ================== /RANK ==================
@bot.tree.command(name="rank", description="Voir le rank RL")
async def rank(interaction: discord.Interaction, player: str):

    await interaction.response.defer(thinking=True)

    try:
        url = f"https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/platform:epic:{player}"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "TRN-Api-Key": TRACKER_API
        }

        r = requests.get(url, headers=headers, timeout=5)

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

    except Exception as e:
        await interaction.followup.send(f"❌ Erreur API : {e}")

# ================== /SHOP ==================
@bot.tree.command(name="shop", description="Boutique RL")
async def shop(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Boutique Rocket League",
        description="https://rl.insider.gg/fr/pc",
        color=0xff9900
    )

    await interaction.response.send_message(embed=embed)

# ================== FLASK (Render fix) ==================
app = Flask("")

@app.route("/")
def home():
    return "Bot is alive"

def run():
    app.run(host="0.0.0.0", port=10000)

Thread(target=run).start()

# ================== START BOT ==================
bot.run(TOKEN)
