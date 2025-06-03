
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import re
from datetime import date
import requests
from bs4 import BeautifulSoup

CHANNEL_ID = 1374105106185719970
HISTORY_FILE = "clan_members.json"
CHANGES_FILE = "zmeny.json"
CLAN_URL = "https://modernarmor.worldoftanks.com/clans/DUKL4/"

def normalize(name):
    return "".join(name.lower().split())

def load_local_members():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_members(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def today = date.today().isoformat()
        joined_data = [{"name": name, "date": today} for name in joined]
        left_data = [{"name": name, "date": today} for name in left]
        save_changes(joined_data, left_data):
    if not os.path.exists(CHANGES_FILE):
        history = {"joined": [], "left": []}
    else:
        with open(CHANGES_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    history["joined"].extend([m for m in joined if m not in history["joined"]])
    history["left"].extend([m for m in left if m not in history["left"]])
    with open(CHANGES_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def fetch_clan_members():
    response = requests.get(CLAN_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    members = []
    rows = soup.select(".styles__StyledTr-sc-1h0c8og-2")
    for row in rows:
        name_elem = row.select_one("a[href^='/profile']")
        role_elem = row.select_one("td:nth-of-type(3)")
        if name_elem and role_elem:
            name = name_elem.text.strip()
            role = role_elem.text.strip()
            members.append({"name": name, "role": role})
    return members

class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def chunk_members(self, members, per_chunk=25):
        chunks = []
        for i in range(0, len(members), per_chunk):
            chunk = members[i:i + per_chunk]
            text = "\n".join([f"✅ {m['name']} – {m['role']}" for m in chunk])
            chunks.append(text)
        return chunks

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje zoznam členov klanu a vypíše ho do kanála.")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        await interaction.response.defer()

        new_members = fetch_clan_members()
        old_members = load_local_members()

        old_dict = {normalize(m["name"]): m["name"] for m in old_members}
        new_dict = {normalize(m["name"]): m["name"] for m in new_members}

        joined = [new_dict[k] for k in new_dict if k not in old_dict]
        left = [old_dict[k] for k in old_dict if k not in new_dict]

        save_members(new_members)
        today = date.today().isoformat()
        joined_data = [{"name": name, "date": today} for name in joined]
        left_data = [{"name": name, "date": today} for name in left]
        save_changes(joined_data, left_data)

        embed = discord.Embed(
            title="📋 Zoznam členov klanu DUKL4",
            description=f"Počet členov: {len(new_members)}",
            color=discord.Color.green()
        )

        # Rozdelenie na polia, každé max 25 mien
        chunks = self.chunk_members(new_members)
        for i, chunk in enumerate(chunks):
            embed.add_field(name=f"Zoznam členov {i+1}" if len(chunks) > 1 else "Zoznam členov", value=chunk, inline=False)

        if joined or left:
            zmeny = []
            if joined:
                zmeny += [f"✅ Nový člen: {name}" for name in joined]
            if left:
                zmeny += [f"❌ Odišiel: {name}" for name in left]
            embed.add_field(name="📝 Zmeny", value="\n".join(zmeny), inline=False)

        channel = self.bot.get_channel(CHANNEL_ID)
        found = False
        async for msg in channel.history(limit=20):
            if msg.author == self.bot.user and msg.embeds and msg.embeds[0].title.startswith("📋 Zoznam členov"):
                await msg.edit(embed=embed)
                found = True
                break
        if not found:
            await channel.send(embed=embed)

        await interaction.followup.send("✅ Zoznam bol úspešne aktualizovaný a zmeny zaznamenané.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClanCog(bot))
