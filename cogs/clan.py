
import discord
from discord.ext import commands
import json
import os

DATA_FILE = "clan_members.json"

class ClanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ensure_data_file()
        print("✅ Clan cog načítaný správne.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Clan cog je pripravený.")

    @commands.command(name="testclan")
    async def test_clan(self, ctx):
        await ctx.send("✅ Clan cog funguje správne.")

    def ensure_data_file(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            print(f"🗂️ Vytvorený prázdny súbor {DATA_FILE}")

async def setup(bot):
    print("🔄 Iniciujem načítanie clan.py")
    await bot.add_cog(ClanCog(bot))
    print("✅ Clan cog úspešne načítaný.")
