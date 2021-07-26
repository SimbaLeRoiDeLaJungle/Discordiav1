import asyncio
from io import BytesIO

import discord
from PIL import Image

from src.GameObject.Map import Map, tiles_path
from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivity
import src.Utilitary as utilis
import asyncio

class SearchTrack(TrackAbstractBase):
    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.message = None
        self.player = Player(ctx.author.id)
        self.dest = None
        self.time_to_search = 5

    async def loop(self):
        def check(reaction, user):
            return str(reaction.emoji) in ["✔", "❌", "▶", "◀"] and user.id == self.player.id and self.message.id == reaction.message.id

        run = True
        pass_next_cause = None
        while run:
            try:
                reaction, _ = await self.bot.wait_for('reaction_add',check=check, timeout=60)
                if str(reaction.emoji) == "✔":
                    await self.player.load(self.bot)
                    if (self.player.pos_x, self.player.pos_y) == self.dest:
                        can_search, curent_activity = self.player.Can(PlayerActivity.SEARCH)
                        if can_search :
                            self.player.SetInfo(activity=PlayerActivity.SEARCH, time_to_search=self.time_to_search)
                            await self.player.save(self.bot)
                            await self.message.edit(content=self.GetContent("\n*** Ta recherce à commencer ! ***"))
                        else:
                            pass_next_cause = curent_activity
                    else:
                        can_moveToSearch , curent_activity = self.player.Can(PlayerActivity.MOVETOSEARCH)
                        if can_moveToSearch:
                            self.player.SetInfo(activity=PlayerActivity.MOVETOSEARCH, time_to_search=self.time_to_search, destination=self.dest)
                            await self.player.save(self.bot)
                            await self.message.edit(content=self.GetContent(f"\n*** Tu es en route pour la zone ({self.dest[0]}, {self.dest[1]}), ta recherce commencera une fois arrivé.***"))
                        else:
                            pass_next_cause = curent_activity

                    run = False

                elif str(reaction.emoji) == "▶":
                    self.time_to_search += 5
                    if self.time_to_search > 40:
                        self.time_to_search = 40
                    await self.message.edit(content=self.GetContent())
                elif str(reaction.emoji) == "◀":
                    self.time_to_search -=5
                    if self.time_to_search < 5:
                        self.time_to_search = 5
                    await self.message.edit(content=self.GetContent())
                else:
                    run = False
            except asyncio.TimeoutError:
                pass
        if pass_next_cause is not None:
            content = self.GetContent()
            if pass_next_cause == PlayerActivity.MOVE:
                content += "\nTu es déja entrain de te déplacer, utilise <!move stop> pour t'arreter ton déplacement."
            elif pass_next_cause == PlayerActivity.MOVETOSEARCH:
                content += "\nTu es déja entrain de te déplacer pour éffectuer une recherche, utilise <!move stop> pour t'arreter ton déplacement."
            elif pass_next_cause == PlayerActivity.SEARCH:
                content += "\n Tu es déja entrain d'effectuer une recherche dans la zone où tu te trouve, il faut que tu attendent la fin de celle-ci"
            await self.message.edit(content=content)
        await self.message.clear_reactions()

    async def load(self, **kwargs):
        self.dest= kwargs.get('pos')
        await self.player.load(self.bot)
        if self.dest is None:
           self.dest = (self.player.pos_x, self.player.pos_y)
        gfx = await self.get_gfx()
        with BytesIO() as image_binary:
            gfx.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(content=self.GetContent(),file=discord.File(fp=image_binary, filename='s.png'))
        await self.message.add_reaction("✔")
        await self.message.add_reaction("❌")
        await self.message.add_reaction("◀")
        await self.message.add_reaction("▶")

    def GetContent(self, end = ""):
        content = f"Veux tu chercher dans la zone : ({self.dest[0]}, {self.dest[1]}) ?\n"
        walk_time_minute = (abs(self.dest[0] - self.player.pos_x) + abs(self.dest[1] - self.player.pos_y)) * self.player.GetTimeForMoveToOneSquare()
        content += f"__temps de marche :__ {utilis.FloatSecondToStr(walk_time_minute*60)}\n"
        content += f"__temps de recherche :__ {self.time_to_search} minutes\n"
        content += end
        return content

    async def get_gfx(self):
        if self.dest != (self.player.pos_x, self.player.pos_y):
            player_gfx = self.player.get_gfx().convert("RGBA")
            dest_type = await Map.GetOneSquareType(self.bot, self.dest)
            current_type = await Map.GetOneSquareType(self.bot, (self.player.pos_x, self.player.pos_y))
            current_square_gfx = Image.open(tiles_path[current_type]).convert("RGBA")
            current_square_gfx = utilis.resize_image(current_square_gfx, 128)
            current_square_gfx.paste(player_gfx, (0,128-64), player_gfx)
            dest_square_gfx = Image.open(tiles_path[dest_type]).convert("RGBA")
            dest_square_gfx = utilis.resize_image(dest_square_gfx, 128)
            arrow = Image.open("images/move.png")
            im = Image.new("RGBA",(500, 200), (255, 0, 0, 0))
            im.paste(current_square_gfx,(0,0), current_square_gfx)
            im.paste(arrow, (128,40), arrow)
            im.paste(dest_square_gfx, (128*2,200-128), dest_square_gfx)
            return im
        else:
            player_gfx = self.player.get_gfx().convert("RGBA")
            current_type = await Map.GetOneSquareType(self.bot, (self.player.pos_x, self.player.pos_y))
            current_square_gfx = Image.open(tiles_path[current_type]).convert("RGBA")
            current_square_gfx = utilis.resize_image(current_square_gfx, 128)
            current_square_gfx.paste(player_gfx, (0,128-64), player_gfx)
            return current_square_gfx