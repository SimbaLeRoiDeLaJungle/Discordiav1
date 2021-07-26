import asyncio
from abc import ABC
from io import BytesIO

import discord

from src.GameObject.Player import Player
from src.GameObject.City import City
import src.Utilitary as utilis
from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Building import Building,BuildingType


class ConstructTrack(TrackAbstractBase):
    async def loop(self):
        content = f"La construction de *{BuildingType.TypeToStr(self.building_type)}* à commencer. Veux tu ajouter un salaire pour les joueurs participant à la construction ?\n" \
                  f"*Si tu ne le fait tu ne risque pas de recevoir beaucoup d'aide pour la construction !*\n" \
                  "__Salaire :__ {} 💰 / point "
        run = True
        apply_sal = False
        salaire = 0
        while run:
            try:
                print(run)
                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r,u: utilis.defaultCheck(r,u, emoji_list=["🔽", "🔼", "⏫", "⏬", "✅",
                                               "❌"], player=self.player, message=self.message), timeout=60*3)
                if reaction.emoji == "🔽":
                    salaire -= 1
                    if salaire<0:
                        salaire = 0
                elif reaction.emoji == "🔼":
                    salaire += 1
                elif reaction.emoji == "⏬":
                    salaire -= 5
                    if salaire<0:
                        salaire = 0
                elif reaction.emoji == "⏫":
                    salaire += 5
                elif reaction.emoji == "✅":
                    run = False
                    apply_sal = True
                else:
                    run = False
                await self.message.edit(content=content.format(salaire))
            except asyncio.TimeoutError:
                pass

        await self.message.clear_reactions()
        await self.city.load(self.bot)
        if apply_sal and salaire>0:
            content = f"La construction de *{BuildingType.TypeToStr(self.building_type)}* à commencer. Veux tu ajouter un salaire pour les joueurs participant à la construction ?\n" \
                      f"*Si tu ne le fait tu ne risque pas de recevoir beaucoup d'aide pour la construction !*\n" \
                      "**__Salaire :__ {} 💰 / point** ✅"
            await self.message.edit(content=content.format(salaire))
            self.city.AddWork('building_construct', {'building_id': self.building.id, 'ppp': salaire})
            await self.city.save(self.bot)
        else:
            content = f"La construction de *{BuildingType.TypeToStr(self.building_type)}* à commencer. Veux tu ajouter un salaire pour les joueurs participant à la construction ?\n" \
                      f"*Si tu ne le fait tu ne risque pas de recevoir beaucoup d'aide pour la construction !*\n" \
                      "__Salaire :__ 0 💰 / point ❌"
            await self.message.edit(content=content.format(salaire))

    async def load(self, **kwargs):
        await self.player.load(self.bot)
        await self.city.load(self.bot)
        self.message = await self.ctx.send(f"La construction de *{BuildingType.TypeToStr(self.building_type)}* à commencer. Veux tu ajouter un salaire pour les joueurs participant à la construction ?\n" \
                  f"*Si tu ne le fait tu ne risque pas de recevoir beaucoup d'aide pour la construction !*\n" \
                  "__Salaire :__ 0 💰 / point ")
        await self.message.add_reaction("⏫")
        await self.message.add_reaction("🔼")
        await self.message.add_reaction("🔽")
        await self.message.add_reaction("⏬")
        await self.message.add_reaction("✅")
        await self.message.add_reaction("❌")
        self.building = await self.city.AddBuilding(self.bot, self.building_type, self.b_city_position)
        if self.building is not None:
           return True
        return False

    def __init__(self, bot, ctx, building_type, b_city_postion):
        super().__init__(bot, ctx)
        self.message = None
        self.player = Player(ctx.author.id)
        self.city = City(ctx.guild.id)
        self.building_type = building_type
        self.b_city_position = b_city_postion
        self.building = None
