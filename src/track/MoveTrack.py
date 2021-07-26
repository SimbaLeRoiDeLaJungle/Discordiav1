import asyncio
from io import BytesIO

import discord
from PIL import Image

from src.GameObject.Map import tiles_path, Map
from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivity
import src.Utilitary as utilis


class MoveTrack(TrackAbstractBase):
    async def loop(self):
        if self.exit_now:
            return None
        def check(reaction, user):
            return str(reaction.emoji) in ["✔",
                                           "❌"] and user.id == self.player.id and reaction.message.id == self.message.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=check, timeout=60 * 2)
            if str(reaction.emoji) == "✔":
                await self.player.load(self.bot)
                can_move, activity = self.player.Can(PlayerActivity.MOVE)
                if can_move:
                    self.player.SetInfo(activity=PlayerActivity.MOVE, destination=self.dest)
                    await self.player.save(self.bot)
                    await self.message.edit(content=self.GetContent(end=True))
                else:
                    await self.message.edit(content = self.GetContent(pass_next=activity, end=False))
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except asyncio.TimeoutError:
            pass



    async def load(self, **kwargs):
        await self.player.load(self.bot)
        if self.dest == (self.player.pos_x,self.player.pos_y):
            await self.ctx.send(f"Tu es déjà dans la zone ({self.player.position_str})")
            self.exit_now = True
            return None
        gfx = await self.get_gfx()
        with BytesIO() as image_binary:
            gfx.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(content=self.GetContent(),file=discord.File(fp=image_binary, filename='s.png'))
        await self.message.add_reaction("✔")
        await self.message.add_reaction("❌")

    def __init__(self, bot, ctx, dest):
        super().__init__(bot, ctx)
        self.message = None
        self.dest = dest
        self.player = Player(ctx.author.id)
        self.exit_now = False
    def GetContent(self, pass_next=None, end=None):
        content = f"{self.player.mention()}\n"
        if pass_next is None or end:
            content += "✔ "
        else:
            content += ""
        content += f"Veux tu te déplacer vers la zone ({self.dest[0]}, {self.dest[1]}) ?\n"
        walk_time_minute = (abs(self.dest[0] - self.player.pos_x) + abs(
            self.dest[1] - self.player.pos_y)) * self.player.GetTimeForMoveToOneSquare()
        content += f"__temps de marche :__ {utilis.FloatSecondToStr(walk_time_minute * 60)}\n"
        if pass_next in [PlayerActivity.MOVE, PlayerActivity.MOVETOSEARCH]:
            current_dest = self.player.info.get('destination')
            content += f"**Tu es actuellement entrain de te déplacer vers la zone ({current_dest[0]}, {current_dest[1]})," \
                       f" tu peux arreter ce déplacement avec la commande <!move stop>. **"
        elif pass_next == PlayerActivity.SEARCH:
            content += f"**Tu es actuellement entrain d'effectuer une recheche, attands la fin de celle-ci pour te déplacer.**"
        if end is not None:
            if end:
                content += "\n **Ton déplacement à commencer !**"
            else:
                content += "\n ** Tu ne peux faire cette action !**"
        return content

    async def get_gfx(self):
        player_gfx = self.player.get_gfx().convert("RGBA")
        dest_type = await Map.GetOneSquareType(self.bot, self.dest)
        current_type = await Map.GetOneSquareType(self.bot, (self.player.pos_x, self.player.pos_y))
        current_square_gfx = Image.open(tiles_path[current_type]).convert("RGBA")
        current_square_gfx = utilis.resize_image(current_square_gfx, 128)
        current_square_gfx.paste(player_gfx, (0, 128 - 64), player_gfx)
        dest_square_gfx = Image.open(tiles_path[dest_type])
        dest_square_gfx = utilis.resize_image(dest_square_gfx, 128)
        arrow = Image.open("images/move.png")
        im = Image.new("RGBA", (500, 200), (255, 0, 0, 0))
        im.paste(current_square_gfx, (0, 0), current_square_gfx)
        im.paste(arrow, (128, 40), arrow)
        im.paste(dest_square_gfx, (128 * 2, 200 - 128), dest_square_gfx)
        return im