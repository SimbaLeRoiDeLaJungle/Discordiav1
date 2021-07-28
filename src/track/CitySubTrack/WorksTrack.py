from src.GameObject.City import City
from src.GameObject.Player import Player, PlayerActivity
from src.GameObject.Building import BuildingType
from src.track.TrackAbstractBase import TrackAbstractBase
import src.Utilitary as utilis
import asyncio


class WorksTrack(TrackAbstractBase):
    async def loop(self):
        run = True
        selected = 0
        passed = False
        time = 5
        while run:
            await self.city.load(self.bot)
            await self.player.load(self.bot)
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r,u : utilis.defaultCheck(r,u,player=self.player,message=self.message, emoji_list=["🔽", "🔼", "✅", "🚪", "➡", "⬅️"]), timeout= 60)
                print(reaction.emoji)
                if str(reaction.emoji) == "🔽":
                    selected += 1

                elif str(reaction.emoji) == "🔼" and selected - 1 >= 0:
                    selected -= 1

                elif str(reaction.emoji) == "✅":
                    run = False
                    passed = True
                elif str(reaction.emoji) == "🚪":
                    run = False

                elif str(reaction.emoji) == "➡":
                    time += 5
                    if time > 60:
                        time = 60
                elif str(reaction.emoji) == "⬅️":
                    time -= 5
                    if time < 5:
                        time = 5

                content = self.GetContent(selected, time)
                await self.message.edit(content=content)
            except asyncio.TimeoutError:
                pass
        if passed:
            await self.player.load(self.bot)
            can_construct, activity = self.player.Can(PlayerActivity.CONSTRUCT)
            if can_construct:
                self.player.SetInfo(activity=PlayerActivity.CONSTRUCT, works=self.city.works['building_construct'][selected],time_to_construct=time)
                await self.player.save(self.bot)
            else:
                pass
        await self.message.delete()

    async def load(self, **kwargs):
        await self.city.load(self.bot)
        await self.player.load(self.bot)
        self.message = await self.ctx.send(self.GetContent(0, 5))
        await self.message.add_reaction("🔼")
        await self.message.add_reaction("🔽")
        await self.message.add_reaction("✅")
        await self.message.add_reaction("🚪")
        await self.message.add_reaction("⬅️")
        await self.message.add_reaction("➡")

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.city = City(ctx.guild.id)
        self.player = Player(ctx.author.id)
        self.message = None

    def GetContent(self, select,time):
        content = "**contstructions :**\n"
        index = 0
        for work in self.city.works['building_construct']:
            for building in self.city.buildings:
                if building.id == work['building_id']:
                    name = BuildingType.TypeToStr(building.building_type)
                    salaire = work['ppp']
                    if index == select:
                        content += "➡️"
                        current_sal = salaire
                    else:
                        content += "- "
                    content += f"_*{name}*_ ({building.city_position[0]}, {building.city_position[1]})\n"
                    content += f"salaire par points : {salaire} 💰\n"
                    content += utilis.MakeLifeBar(building.info['life'], building.info['max_life']) + "\n"
                    content += "---------------\n"
                    index += 1
                    break
        content += "回~回~回~回~\n"
        content += f"__temps de travail :__ **{time}** minutes (⬅️ ➡️)\n"

        estimation_pts = self.player.GetConstructPointPerMinutes()*time
        content += f"__Estimation :__ {estimation_pts} point(s) (**{round(estimation_pts*current_sal, 0)}**💰)\n"
        return content
