import asyncio
import json
from io import BytesIO

import discord

from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivity
from PIL import Image, ImageFont, ImageDraw
import src.Utilitary as utilis


class CoffreTrack(TrackAbstractBase):
    max_col = 7
    begin = (6, 24)
    item_size = (15, 15)
    perso_pos = (128, 15)
    perso_size = (50, 50)
    txt_padding = (70, 8)
    txtb = (128, 85)
    eqp_pos = {'head': (208, 11), '2hands': (230, 49), 'lhand': (230, 49), 'rhand': (187, 49), 'armor': (218, 30),
               'tenue': (202, 30), 'torso': (201, 30), 'legs': (211, 51), 'pads': (209, 67)}
    comp_pos = {"medecine": (txtb[0] + txt_padding[0], txtb[1]),
                "recherche": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1]),
                "bucherons": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1] * 2),
                "mineur": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1] * 3),
                "forgeron": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1] * 4),
                "constructeur": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1] * 5),
                "movement": (txtb[0] + txt_padding[0], txtb[1] + +txt_padding[1] * 6),
                "craft": (txtb[0] + txt_padding[0], txtb[1] + txt_padding[1] * 7)}

    fcomp_pos = {"attaque": txtb, "defense": (txtb[0], txtb[1] + txt_padding[1]),
                 "esquive": (txtb[0], txtb[1] + txt_padding[1] * 2), "vitesse": (txtb[0], txtb[1] + txt_padding[1] * 3)}

    async def loop(self):
        def check(m):
            return m.content.startswith(">>") and m.channel.id == self.ctx.channel.id and m.author.id == self.player.id

        run = True
        while run:
            stop = await self.player.AsToStopUserTask(self.bot, self.task_id)
            if stop:
                break
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=15)
                stop = await self.player.AsToStopUserTask(self.bot, self.task_id)
                if stop:
                    break
                command = msg.content.split()
                req = command[0][2:]
                if req == 'set':
                    pos_str = command[1]
                    line = utilis.str_to_int(pos_str[0])
                    col = int(pos_str[1]) - 1
                    index = line * CoffreTrack.max_col + col
                    await self.player.load(self.bot)
                    if self.player.info['activity'] in [int(PlayerActivity.MOVE), int(PlayerActivity.MOVETOSEARCH)]:
                        await self.message.edit(
                            content="Tu es actuellement en mouvement, attends d'être arriver pour changer ton équipement.")
                    else:
                        if index < len(self.coffre['equipments']):
                            if self.coffre['equipments'][index].sex is None or self.coffre['equipments'][index].sex == self.player.sex:
                                await self.player.Equip(self.bot, self.coffre['equipments'][index].id)
                                await self.player.save(self.bot)
                                await self.message.delete()
                                await self.load()
                            else:
                                if self.player.sex:
                                    content = f"**L'object choisi :  {self.coffre['equipments'][index].name} ne peut pas être équipé par un homme."
                                else:
                                    content = f"**L'object choisi :  {self.coffre['equipments'][index].name} ne peut pas être équipé par une femme."
                                await self.message.edit(content=content)
                        else:
                            if index < len(self.coffre['equipments']) + len(self.coffre['consumable']):
                                content = f"**L'object choisi :  {self.coffre['consumable'][index].name} ne peut pas être équipé.**"
                            elif index < len(self.coffre['equipments']) + len(self.coffre['consumable']) + len(self.coffre['basic_obj']):
                                content = f"**L'objet choisi : {self.coffre['basic_obj'][index].name} ne peut pas être équipé.**"
                            else:
                                content = "**Tu a commis une erreur dans l'objet à équipé**"
                            await self.message.edit(content=content)
                if req == 'close':
                    run = False

                elif req == "see":
                    pos_str = command[1]
                    line = utilis.str_to_int(pos_str[0])
                    col = int(pos_str[1]) - 1
                    index = line * CoffreTrack.max_col + col
                    if index < len(self.coffre['equipments']):
                        obj = self.coffre['equipments'][index]
                    elif index < len(self.coffre['consumable']) + len(self.coffre['consumable']):
                        i = index - len(self.coffre['equipments'])
                        obj = self.coffre['consumable'][i]
                    elif index < len(self.coffre['consumable']) + len(self.coffre['consumable']) + len(self.coffre['basic_obj']):
                        i = index - len(self.coffre['equipments']) - len(self.coffre['consumable'])
                        obj = self.coffre['basic_obj'][i]
                    im = utilis.GetObjectsInfoGfx([obj])
                    with BytesIO() as image_binary:
                        im.save(image_binary, format='PNG')
                        image_binary.seek(0)
                        await self.ctx.send(f"{self.ctx.author.mention}", file=discord.File(fp=image_binary, filename='s.png'))

            except asyncio.TimeoutError:
                pass


        try:
            await self.message.delete()

        except discord.NotFound:
            pass

    async def load(self, **kwargs):

        self.player = Player(self.ctx.author.id)
        await self.player.StopAllUserTasks(self.bot)
        await self.player.load(self.bot)
        self.coffre = await self.player.GetCoffre(self.bot)
        im = self.get_gfx()
        with BytesIO() as image_binary:
            im.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(f"{self.ctx.author.mention}",
                                               file=discord.File(fp=image_binary, filename='s.png'))
        self.task_id = self.message.id

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.player = None
        self.message = None
        self.coffre = {'equipment': [], 'consumable': dict()}
        self.task_id = None


    def get_gfx(self):
        base_path = "images/inventory_preset.png"
        im = Image.open(base_path)
        beg = CoffreTrack.begin
        coffre_gfx = utilis.GetCoffreGfx(self.coffre, money=self.player.money).convert("RGBA")
        im.paste(coffre_gfx, beg, coffre_gfx)
        font = ImageFont.truetype("font/Nouveau_IBM.ttf", 9)
        draw = ImageDraw.Draw(im)
        dcomp = {"medecine": 0, "recherche": 0, "bucherons": 0, "mineur": 0, "forgeron": 0, "constructeur": 0,
                 "movement": 0,
                 "craft": 0}
        dfcomp = {"attaque": 0, "defense": 0, "esquive": 0, "vitesse": 0}
        for key, value in self.player.equipments['items'].items():
            if value is not None:
                gfx = utilis.resize_image(value.get_gfx(crop=True), CoffreTrack.item_size[0])
                im.paste(gfx, CoffreTrack.eqp_pos[key], gfx)
                if value.fight_comp is not None:
                    for k, v in value.fight_comp.items():
                        dfcomp[k] += v
                if value.comp is not None:
                    for k, v in value.comp.items():
                        dcomp[k] += v

        for key, value in self.player.fight_comp.items():
            if dfcomp[key] > 0:
                txt = f"{utilis.keyToAbrev(key)} {value + dfcomp[key]}(+{dfcomp[key]})"
            elif dfcomp[key] < 0:
                txt = f"{utilis.keyToAbrev(key)}{value + dfcomp[key]}({dfcomp[key]})"
            else:
                txt = f"{utilis.keyToAbrev(key)} {value}"
            draw.text(CoffreTrack.fcomp_pos[key], txt, font=font, stroke_width=1, stroke_fill="black")
        for key, value in self.player.comp.items():
            if dcomp[key] > 0:
                txt = f"{utilis.keyToAbrev(key)} {value + dcomp[key]}(+{dcomp[key]})"
            elif dcomp[key] < 0:
                txt = f"{utilis.keyToAbrev(key)} {value + dcomp[key]}({dcomp[key]})"
            else:
                txt = f"{utilis.keyToAbrev(key)} {value}"
            draw.text(CoffreTrack.comp_pos[key], txt, font=font, stroke_width=1, stroke_fill="black")

        gfx = utilis.resize_image(self.player.get_gfx(), CoffreTrack.perso_size[0])
        im.paste(gfx, CoffreTrack.perso_pos, gfx)
        return utilis.resize_image(im, 500)
