
import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
from bs4 import BeautifulSoup
import os

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

def save_changes(joined, left):
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
        save_changes(joined, left)

        # Priprav správu
        embed = discord.Embed(title="📋 Zoznam členov klanu DUKL4", color=0x00ff00)
        for member in new_members:
            embed.add_field(name=member["name"], value=member["role"], inline=False)

        # Prepíš existujúcu správu v kanáli (ak existuje)
        channel = self.bot.get_channel(CHANNEL_ID)
        async for msg in channel.history(limit=20):
            if msg.author == self.bot.user and msg.embeds and msg.embeds[0].title == "📋 Zoznam členov klanu DUKL4":
                await msg.edit(embed=embed)
                break
        else:
            await channel.send(embed=embed)

        await interaction.followup.send("✅ Zoznam bol úspešne aktualizovaný a zmeny zaznamenané.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClanCog(bot))
