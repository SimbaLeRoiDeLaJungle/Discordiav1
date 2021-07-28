import asyncio

from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.City import City
from src.GameObject.Player import Player
from src.track.CitySubTrack.BuildingInfoTrack import BuildingInfoTrack


class CityInfoTrack(TrackAbstractBase):

    async def loop(self):
        def check(message):
            return message.content.startswith(">>") and message.author.id == self.player.id
        run = True
        while run:
            stop = await self.player.AsToStopUserTask(self.bot, self.task_id)
            if stop:
                break
            try:
                user_message = await self.bot.wait_for('message', check=check, timeout=60*2)
                stop = await self.player.AsToStopUserTask(self.bot, self.task_id)
                if stop:
                    break
                arguments = user_message.content.split()
                command = arguments[0][2:]
                arguments = arguments[1:]
                await self.city.load(self.bot)
                if command == "info":
                    if len(arguments) == 2:
                        try:
                            city_pos = int(arguments[0]), int(arguments[1])
                        except:
                            await self.message.edit(content=self.GetContent(user_error="Tu as commis une erreur de syntaxe"))
                        else:
                            building = None
                            for building in self.city.buildings:
                                if city_pos == building.city_position:
                                    break
                                else:
                                    building =None
                            if building is None:
                                await self.message.edit(content=self.GetContent(user_error="Le batiments que tu recherche n'existe pas"))
                            else:
                                await self.message.edit(content=self.GetContent())
                                track = BuildingInfoTrack(self.bot, self.ctx, building)
                                await track.load()
                                await track.loop()
                    else:
                        await self.message.edit(content=self.GetContent(user_error="Tu as commis une erreur de syntaxe"))
                elif command == "close":
                    run = False
                else:
                    await self.message.edit(content=self.GetContent(user_error="Tu as commis une erreur de syntaxe"))
            except asyncio.TimeoutError:
                pass


    async def load(self, **kwargs):
        await self.player.load(self.bot)
        await self.player.StopAllUserTasks(self.bot)
        await self.city.load(self.bot)
        self.message = await self.ctx.send(self.GetContent())
        self.task_id = self.message.id
        await Player.AddUserTask(self.bot, self.task_id, self.player.id)

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.city = City(ctx.guild.id)
        self.player = Player(ctx.author.id)
        self.message = None
        self.task_id = None

    def GetContent(self, user_error=None):
        content = "**__Resources :__**\n"
        content += f"bois : {self.city.resource_info['wood']}\n"
        content += f"metals : {self.city.resource_info['metal']}\n"
        content += f"pierres : {self.city.resource_info['rock']}\n"
        content += f"nouritures : {self.city.resource_info['food']}\n"
        content += f"argents : {self.city.resource_info['money']}\n"
        content += "------------------\n"
        content += "**utilise : >>info X Y** *pour avoir des information sur le batiments en position (X,Y)*\n"
        if user_error is not None:
            content += "------------------\n"
            content += f"*{user_error}*\n"
        return content