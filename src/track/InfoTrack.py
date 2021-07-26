from io import BytesIO

import discord
from PIL import Image

from src.GameObject.City import City
from src.GameObject.Map import Map, tiles_path
from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivityToString, PlayerActivity
import src.Utilitary as utilis
from datetime import datetime,timedelta


class InfoTrack(TrackAbstractBase):
    async def loop(self):
        pass

    async def load(self, **kwargs):
        await self.player.load(self.bot)
        city = await City.GetCityByPosition(self.bot, self.player.position)
        gfx = await self.get_gfx()
        with BytesIO() as image_binary:
            gfx.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(content=self.GetContent(city),file=discord.File(fp=image_binary, filename='s.png'))

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.player = Player(ctx.author.id)
        self.message = None

    def GetContent(self, city):
        content = f"{self.player.mention()}\n"
        content += f"__position :__ {self.player.position_str}\n"
        activity = self.player.info['activity']
        content += f"__activitée :__ {PlayerActivityToString(activity)}\n"
        if activity == PlayerActivity.MOVE:
            dest = self.player.info['destination']
            content += f"__arrivée dans :__ {utilis.FloatSecondToStr(self.player.estimate_time_from_distance()*60)} (estimation)\n"
            content += f"__destination :__ ({dest[0]}, {dest[1]})"
        if activity == PlayerActivity.MOVETOSEARCH:
            dest = self.player.info['destination']
            content += f"__arrivée dans :__ {utilis.FloatSecondToStr(self.player.estimate_time_from_distance()*60)} (estimation)\n"
            content += f"__durée de la recherche :__ {utilis.FloatSecondToStr(self.player.info['time_to_search']*60)}"
            content += f"__destination :__ ({dest[0]}, {dest[1]})"
        if activity == PlayerActivity.SEARCH:
            b_time = utilis.formatStrToDate(self.player.info["time_begin_search"])
            delta = timedelta(minutes=self.player.info['time_to_search'])
            end_time = b_time + delta
            now = datetime.now()
            rest = (end_time-now).total_seconds()
            if rest<0:
                rest=0
            content += f"__fin dans :__ {utilis.FloatSecondToStr(rest)}\n"
        if city is not None:
            content += f"Tu peux rentrer dans la ville : **{city.name}** en rejoignant le serveur suivant : {city.invite_link}"

        return content

    async def get_gfx(self):
        player_gfx = self.player.get_gfx().convert("RGBA")
        square_type = await Map.GetOneSquareType(self.bot, self.player.position)
        square_gfx = Image.open(tiles_path[square_type]).convert("RGBA")
        square_gfx = utilis.resize_image(square_gfx, 128)
        square_gfx.paste(player_gfx, (0, 128 - 64), player_gfx)
        return square_gfx