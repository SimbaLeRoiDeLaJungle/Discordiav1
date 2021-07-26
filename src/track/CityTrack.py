import asyncio
from io import BytesIO

import discord
import src.Utilitary as utilis
from src.track.CitySubTrack.WorksTrack import WorksTrack
from src.track.TrackAbstractBase import TrackAbstractBase

from src.GameObject.Player import Player
from src.GameObject.City import City

class CityTrack(TrackAbstractBase):
    async def loop(self):
        try:
            reaction, _ = await self.bot.wait_for('reaction_add',check= lambda r,u: utilis.defaultCheck(r, u, player=self.player, message=self.message, emoji_list=["0️⃣", "1️⃣"]))
            if str(reaction.emoji) == "0️⃣":
                track = WorksTrack(self.bot, self.ctx)
                await track.load()
                await track.loop()
            elif str(reaction.emoji) == "1️⃣":
                pass

        except asyncio.TimeoutError:
            pass

    async def load(self, **kwargs):
        await self.city.load(self.bot)
        await self.player.load(self.bot)
        if self.player.position == self.city.position:
            gfx = self.city.get_gfx()
            with BytesIO() as image_binary:
                gfx.save(image_binary, format='PNG')
                image_binary.seek(0)
                self.message = await self.ctx.send(content=self.GetContent(), file=discord.File(fp=image_binary, filename='s.png'))
            await self.message.add_reaction("0️⃣")
            await self.message.add_reaction("1️⃣")

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.message = None
        self.player = Player(self.ctx.author.id)
        self.city = City(self.ctx.guild.id)

    def GetContent(self):
        content = "0️⃣ travails\n"
        content += "1️⃣ forge\n"
        return content