
import discord
from discord import app_commands
from discord.ext import commands
import json
import requests
from bs4 import BeautifulSoup
import os

class Zoznam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.add_command(self.aktualizuj_zoznam)

    @app_commands.command(name="aktualizuj_zoznam", description="Aktualizuje zoznam členov klanu DUKL4")
    async def aktualizuj_zoznam(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            response = requests.get("https://console.worldoftanks.com/clans/231141/", timeout=3)
            soup = BeautifulSoup(response.text, "html.parser")

            member_elements = soup.select(".clan-member")
            new_members = []

            for element in member_elements:
                name_elem = element.select_one(".clan-member__name")
                role_elem = element.select_one(".clan-member__role")
                if name_elem and role_elem:
                    name = name_elem.text.strip()
                    role = role_elem.text.strip()
                    new_members.append({"name": name, "role": role})

            if not os.path.exists("clan_members.json"):
                old_members = []
            else:
                with open("clan_members.json", "r", encoding="utf-8") as f:
                    old_members = json.load(f)

            old_names = {m["name"] for m in old_members}
            new_names = {m["name"] for m in new_members}

            joined = new_names - old_names
            left = old_names - new_names

            if joined or left:
                with open("clan_members.json", "w", encoding="utf-8") as f:
                    json.dump(new_members, f, ensure_ascii=False, indent=2)

            message = "✅ Zoznam členov bol aktualizovaný."
            if joined:
                message += f"\n🟢 Noví členovia: {', '.join(joined)}"
            if left:
                message += f"\n🔴 Odišli: {', '.join(left)}"

        except requests.exceptions.Timeout:
            message = "❌ Chyba: Server WoT neodpovedá (timeout)."
        except Exception as e:
            message = f"❌ Chyba pri aktualizácii zoznamu: {e}"

        await interaction.followup.send(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Zoznam(bot))
