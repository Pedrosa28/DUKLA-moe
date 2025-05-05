
import json
from discord.ext import commands
import discord

class Moe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("data.json", "r", encoding="utf-8") as file:
            self.data = json.load(file)

    @commands.command(name="moe")
    async def get_moe(self, ctx, *, tank_name: str):
        tank_name = tank_name.lower()
        matches = [tank for tank in self.data if tank_name in tank["Name"].lower()]
        if not matches:
            await ctx.send(f"Nenašiel sa žiadny tank s názvom obsahujúcim: `{tank_name}`.")
            return

        tank = matches[0]
        embed = discord.Embed(title=tank["Name"], color=discord.Color.green())
        embed.add_field(name="Tier", value=tank.get("Tier", "N/A"))
        embed.add_field(name="Battles", value=tank.get("Battles", "N/A"))
        embed.add_field(name="1 MoE", value=tank.get("1 MoE", "N/A"))
        embed.add_field(name="2 MoE", value=tank.get("2 MoE", "N/A"))
        embed.add_field(name="3 MoE", value=tank.get("3 MoE", "N/A"))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moe(bot))
