
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import json
import os
import asyncio
import aiohttp

CLAN_URL = "https://modernarmor.worldoftanks.com/en/clans/DUKL4/"
PLAYER_STATS_URL = "https://wotstars.com/playerstats/{}/"
DATA_FILE = "clan_members.json"
CHANNEL_ID = 1374105106185719970

ROLE_ORDER = {
    "Commander": 1,
    "Deputy Commander": 2,
    "Executive Officer": 3,
    "Recruitment Officer": 4,
    "Private Member": 5
}

HEADERS = {
    "User-Agent": "DUKLA-Moe-Bot",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.semaphore = asyncio.Semaphore(2)  # Limit simultaneous requests
        self.update_clan_members.start()
        print("✅ Clan cog načítaný správne.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Clan cog je pripravený.")

    @commands.command(name="testclan")
    async def test_clan(self, ctx):
        await ctx.send("✅ Clan cog funguje správne.")

    def get_wn8_color(self, wn8):
        try:
            wn8 = float(wn8.replace(",", ""))
            if wn8 >= 2900:
                return 0x9900FF  # Super Unicum (Fialová)
            elif wn8 >= 2450:
                return 0x5555FF  # Unicum (Tmavomodrá)
            elif wn8 >= 1850:
                return 0x00AAFF  # Modrá
            elif wn8 >= 1450:
                return 0x00FF00  # Zelená
            elif wn8 >= 900:
                return 0xFFFF00  # Žltá
            else:
                return 0xFF5500  # Oranžová
        except ValueError:
            return 0x888888  # Šedá, ak nie je platná hodnota

    async def get_player_wn8(self, session, player_name):
        try:
            player_url = PLAYER_STATS_URL.format(player_name.replace(" ", ""))
            async with self.semaphore:
                async with session.get(player_url, headers=HEADERS) as response:
                    if response.status == 200:
                        soup = BeautifulSoup(await response.text(), "html.parser")
                        wn8_element = soup.find("div", {"class": "wn8"})
                        if wn8_element:
                            return wn8_element.text.strip()
                        else:
                            return "N/A"
                    else:
                        print(f"⚠️ Chyba {response.status} pri načítavaní WN8 pre {player_name}")
                        return "N/A"
        except Exception as e:
            print(f"❌ Chyba pri načítavaní WN8 pre {player_name}: {e}")
            return "N/A"

    def load_previous_members(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_members(self, members):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(members, f, ensure_ascii=False, indent=4)

    @tasks.loop(hours=24)
    async def update_clan_members(self):
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                response = await session.get(CLAN_URL)
                if response.status != 200:
                    print(f"⚠️ Chyba {response.status} pri načítavaní zoznamu členov.")
                    return

                soup = BeautifulSoup(await response.text(), "html.parser")
                members_table = soup.find("div", {"id": "list-box_members"})

                if not members_table:
                    print("⚠️ Nenašiel som zoznam členov.")
                    return

                rows = members_table.find_all("tr")
                current_members = [{"name": row["data-name"], "role": row["data-role-name"]} for row in rows]

                previous_members = self.load_previous_members()
                previous_names = {member["name"] for member in previous_members}
                current_names = {member["name"] for member in current_members}

                joined = current_names - previous_names
                left = previous_names - current_names

                self.save_members(current_members)

                sorted_members = sorted(current_members, key=lambda x: ROLE_ORDER.get(x["role"], 99))

                embed = discord.Embed(
                    title="🛡️ DUKLA Československo [DUKL4] - Členovia",
                    description=f"Počet členov: **{len(sorted_members)}**",
                    color=0xFFD700
                )

                tasks = [self.get_player_wn8(session, member["name"]) for member in sorted_members]
                wn8_values = await asyncio.gather(*tasks)

                for member, wn8_value in zip(sorted_members, wn8_values):
                    name = member["name"]
                    role = member["role"]
                    color = self.get_wn8_color(wn8_value)

                    embed.add_field(
                        name=f"✅ {name}",
                        value=f"🛡️ **Rola:** {role}
🎯 **WN8:** {wn8_value}",
                        inline=False
                    )

                channel = self.bot.get_channel(CHANNEL_ID)
                if channel:
                    async for message in channel.history(limit=10):
                        if message.author == self.bot.user:
                            await message.delete()

                    await channel.send(embed=embed)

        except Exception as e:
            print(f"❌ Chyba pri aktualizácii členov: {e}")

async def setup(bot):
    await bot.add_cog(ClanCog(bot))
