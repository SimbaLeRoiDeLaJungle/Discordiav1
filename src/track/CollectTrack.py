import asyncio

import discord

from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivity
from src.GameObject.Map import Map, SquareType, GetSquareTypeStr
import src.Utilitary as utilis

class CollectTrack(TrackAbstractBase):
    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.message = None
        self.player = Player(ctx.author.id)
        self.squareType = None
        self.task_id

    async def loop(self):
        try :
            reaction, _ = await self.bot.wait_for('reaction_add', check = lambda r,u: utilis.defaultCheck(r,u,player=self.player,message=self.message), timeout=60*3)
            if str(reaction.emoji) == "✔":
                await self.player.load(self.bot)
                self.squareType = await Map.GetOneSquareType(self.bot, self.player.position)
                if self.squareType in [SquareType.WOOD, SquareType.ROCK, SquareType.METAL]:
                    can_collect, activity = self.player.Can(PlayerActivity.COLLECT)
                    if can_collect:
                        self.player.SetInfo(activity=PlayerActivity.COLLECT, square_type=self.squareType)
                        await self.player.save(self.bot)
                        content = self.message.content
                        content += "\n Tu a commencer a collecter des resources."
                        await self.message.edit(content=content)

                    else:
                        content = self.message.content
                        content += "\nTu es déjà dans une activité, fini celle-ci puis réessaye après"
                        await self.message.edit(content=content)
                else:
                    content = self.message.content
                    content += "\nIl n'y a rien a collecter dans la zone où tu te trouve."
                    await self.message.edit(content=content)
                await asyncio.sleep(10)
        except asyncio.TimeoutError:
            pass
        try:
            await self.message.delete()
        except discord.NotFound:
            pass
        await self.player.DeleteUserTask(self.bot, self.task_id)

    async def load(self, **kwargs):
        await self.player.load(self.bot)
        self.squareType = await Map.GetOneSquareType(self.bot, self.player.position)
        if self.squareType in [SquareType.WOOD, SquareType.ROCK, SquareType.METAL]:
            can_collect, activity = self.player.Can(PlayerActivity.COLLECT)
            square_type_string = GetSquareTypeStr(self.squareType, pre=True)
            if can_collect:
                self.message = await self.ctx.send(f"{self.player.mention()}, veux tu commencer a collecter {square_type_string}?")
                await self.message.add_reaction("✔")
                await self.message.add_reaction("❌")
                self.task_id = self.message.id
                await Player.AddUserTask(self.bot, self.player.id, self.task_id)
                return True
            else:
                self.message = await self.ctx.send(f"{self.player.mention()}, tu es déjà dans une activité, fini celle-ci puis réessaye après")
                return False
        else:
            await self.ctx.send(f"{self.player.mention()}, il n'y a rien a collecter dans la zone où tu te trouve.")
            return False