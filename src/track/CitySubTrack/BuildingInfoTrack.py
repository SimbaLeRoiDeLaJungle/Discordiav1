import asyncio
from io import BytesIO

import discord

from src.GameObject.Building import BuildingType
from src.GameObject.Player import Player, PlayerActivity
from src.track.TrackAbstractBase import TrackAbstractBase
import src.Utilitary as utilis


class BuildingInfoTrack(TrackAbstractBase):

    async def loop(self):
        validate = False
        time = 5
        run = not self.building.is_construct
        while run:
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r,u: utilis.defaultCheck(r, u, player=self.player, message=self.message, emoji_list=["✔", "❌", "◀", "▶"]),timeout=60*3)
                if str(reaction.emoji) == "✔":
                    validate = True
                    run = False
                elif str(reaction.emoji) == "◀":
                    time -= 5
                    if time < 5:
                        time = 5
                elif str(reaction.emoji) == "▶":
                    time += 5
                    if time > 60:
                        time = 60
                else:
                    run = False
            except asyncio.TimeoutError:
                pass
            finally:
                await self.message.edit(content=self.GetContent(time))
        if validate:
            await self.player.load(self.bot)
            can_construct, activity = self.player.Can(PlayerActivity.CONSTRUCT)
            if can_construct:
                self.player.SetInfo(activity=PlayerActivity.CONSTRUCT, works={'ppp':0, 'building_id':self.building.id}, time_to_construct=time)
                await self.player.save(self.bot)
                content = self.GetContent(time) + "\n **Tu as commencer a construire ce batiments.**"
                await self.message.edit(content=content)
            else:
                content = self.GetContent(time) + "\n **Tu es déjà en activitée, tu ne peux donc pas participer a la construction pour l'instant."
                await self.message.edit(content=content)
        else:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass

    async def load(self, **kwargs):
        await self.building.load(self.bot)
        await self.player.load(self.bot)
        gfx = self.building.get_gfx()
        with BytesIO() as image_binary:
            gfx.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(content=self.GetContent(5),
                                               file=discord.File(fp=image_binary, filename='s.png'))
        if not self.building.is_construct:
            await self.message.add_reaction("✔")
            await self.message.add_reaction("❌")
            await self.message.add_reaction("◀")
            await self.message.add_reaction("▶")

    def __init__(self, bot, ctx, building):
        super().__init__(bot, ctx)
        self.building = building
        self.message = None
        self.player = Player(ctx.author.id)

    def GetContent(self, time):
        content = f"{BuildingType.TypeToStr(self.building.building_type)}\n"
        content += self.building.lifeBar
        if not self.building.is_construct:
            content += f"Veux tu aider à la construction de ce batiments gratuitement ?\n"
            content += f"temps : {time} minutes\n"
            content += "*Si tu veux un salaire va voir le travail disponible !*"
        return content