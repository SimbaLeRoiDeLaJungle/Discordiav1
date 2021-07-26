import asyncio
from io import BytesIO
from PIL import Image
import discord

from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player
from src.GameObject.Equipment import Equipment


class StartTrack(TrackAbstractBase):
    intro = "Bienvenue à **Discordia** étranger ! \n"
    end = "__Ton inscription est validée__, une grande aventure t'attends !\n"
    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.message = None
        self.player = None

    async def loop(self):
        def check_hair_color(reaction, user):
            return str(reaction.emoji) in ["⬛","🟨","🟫"] and user.id == self.player.id
        def check_sex(reaction, user):
            return user.id == self.player.id and str(reaction.emoji) in ["♀", "♂"]
        pa = True
        await self.message.edit(content=StartTrack.intro + "**👉 Choisi ton sexe **\n")
        try :
            reaction, _ = await self.bot.wait_for('reaction_add', check=check_sex, timeout=3*60)
            print(str(reaction))
            if "♂" == str(reaction.emoji):
                self.player.sex = True
                self.player.equipments['attribute']['hair'] = 'milong'
            elif "♀" == str(reaction.emoji):
                self.player.sex = False
                self.player.equipments['attribute']['hair'] = "princesse"
            semo = str(reaction)
        except asyncio.TimeoutError:
            await self.message.delete()
            pa = False
            semo =""

        if pa:
            await self.message.edit(content=StartTrack.intro + f"{semo} Choisi ton sexe.\n **👉 Choisi la couleur de tes cheveux.**")
            await self.message.clear_reactions()
            await self.message.add_reaction("⬛")
            await self.message.add_reaction("🟨")
            await self.message.add_reaction("🟫")
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=check_hair_color, timeout=3*60)
                if str(reaction.emoji) == "⬛":
                    self.player.equipments['attribute']['hair_color'] = 'black'
                elif str(reaction.emoji) == "🟫":
                    self.player.equipments['attribute']['hair_color'] = 'brown'
                elif str(reaction.emoji) == "🟨":
                    self.player.equipments['attribute']['hair_color'] = 'blond'
            except asyncio.TimeoutError:
                await self.message.delete()
                pa = False

        if pa:
            if self.player.sex:
                first_pants = await Equipment.GetSpecimen(self.bot, 'black-toge')
                first_pants.user_id = self.player.id
                await first_pants.store(self.bot)
                self.player.SetEquipment(first_pants)
            else:
                first_tenue = await Equipment.GetSpecimen(self.bot, 'red-elegante-robe')
                first_tenue.user_id = self.player.id
                await first_tenue.store(self.bot)
                self.player.SetEquipment(first_tenue)
            await self.player.store(self.bot)
            await self.message.delete()
            result = self.player.get_gfx()
            with BytesIO() as image_binary:
                result.save(image_binary, format='PNG')
                image_binary.seek(0)
                await self.ctx.send(f"{self.ctx.author.mention}, {StartTrack.end}", file=discord.File(fp=image_binary, filename='s.png'))

    async def load(self, **kwargs):
        self.player = Player(self.ctx.author.id)
        is_in_db = await self.player.is_in_db(self.bot)
        if not is_in_db:
            self.player.guild_id = self.ctx.guild.id
            im= Image.open("images/ban.png")
            with BytesIO() as image_binary:
                im.save(image_binary, format='PNG')
                image_binary.seek(0)
                self.message = await self.ctx.send(StartTrack.intro, file=discord.File(fp=image_binary, filename='s.png'))
            await self.message.add_reaction("♀")
            await self.message.add_reaction("♂")
            return True
        return False
