import asyncio
from io import BytesIO

import discord
from PIL import Image

import src.Utilitary as utilis
from src.track.CoffreTrack import CoffreTrack

from src.track.TrackAbstractBase import TrackAbstractBase
from src.GameObject.Player import Player, PlayerActivity
from src.GameObject.Seller import Seller


class SellerTrack(TrackAbstractBase):

    async def loop(self):
        def check(message):
            return message.content.startswith(">>") and message.channel.id == self.ctx.channel.id and message.author.id == self.player.id
        run = True
        while run:
            try:
                message = await self.bot.wait_for('message', check=check, timeout=60*3)
                exist = await self.seller.Exist(self.bot)
                arguments = message.content.split()
                command = arguments[0][2:]
                print(command)
                content_error = None
                error = False
                if not exist:
                    run = False
                    await self.message.edit(content=f"**Pas de chance, le vendeur vien de partir ...**")
                    await asyncio.sleep(15)
                    await self.message.delete()
                else:
                    if command == "buy":
                        try:
                            pos = int(arguments[1])-1
                        except Exception as e:
                            error = True
                            content_error = "erreur de syntaxe pour le choix de l'object à acheter."
                            pos = None
                        print(f'pos : {pos}')
                        if pos is not None:
                            if pos < len(self.seller.info['equipments']):
                                obj = self.seller.info['equipments'][pos]
                            elif pos < len(self.seller.info['basic_obj'])+len(self.seller.info['equipments']):
                                obj = self.seller.info['basic_obj'][pos-len(self.seller.info['equipments'])]
                            elif pos < len(self.seller.info['basic_obj']) + len(self.seller.info['consumable'])+len(self.seller.info['equipments']):
                                obj = self.seller.info['consumable'][pos-(len(self.seller.info['basic_obj'])+len(self.seller.info['equipments']))]
                            else:
                                error = True
                                content_error = "erreur de syntaxe pour le choix de l'object à acheter."
                                obj = None
                            print(f"name : {obj.name}")
                            if obj is not None:
                                price = self.seller.get_price(obj)
                                await self.player.load(self.bot)
                                activity = self.player.info['activity']
                                if activity == int(PlayerActivity.WAIT):
                                    if self.player.money >= price:
                                        self.player.money -= price
                                        await self.player.save(self.bot)
                                        await Player.AddEquipementsToCoffre(self.bot, self.player.id, [obj])
                                    else:
                                        error = True
                                        content_error = "Tu n'as pas assez d'argents pour acheter cet object."
                                else:
                                    error=True
                                    content_error = "Tu es acutellement entrain de faire une activitée, attends la fin de celle-ci pour acheter ou vendre des objets."
                        if not error:
                            await self.message.delete()
                            await self.load()
                        else:
                            await self.message.edit(content = f"**{content_error}**")
                    elif command == "sell":
                        try:
                            line = int(arguments[1])-1
                            col = int(arguments[2])-1
                            print(f"line : {line}")
                        except Exception as e:
                            error = True
                            content_error = "erreur de syntaxe pour le choix de l'object à vendre."
                            line = None
                            col = None
                        obj = None
                        if line is not None:
                            index = line * CoffreTrack.max_col + col
                            if 0<= index< len(self.coffre['equipments']):
                                obj = self.coffre['equipments'][index]
                            elif index < len(self.coffre['equipments']) + len(self.coffre['consumable']):
                                obj = self.coffre['consumable'][index-len(self.coffre['equipments'])]
                            elif index < len(self.coffre['equipments']) + len(self.coffre['basic_obj']) + len(self.coffre['consumable']):
                                obj = self.coffre['basic_obj'][index - len(self.coffre['equipments']) - len(self.coffre['consumable'])]
                            else:
                                error = True
                                content_error = "erreur dans le choix de l'object à vendre."
                                obj = None
                        if obj is not None:
                            price = self.seller.get_price(obj, mode='buy_price')
                            msg = await self.ctx.send(f"{self.player.mention()} confirme tu la vente de {obj.name} pour le prix de {price} pièces d'or ?")
                            await msg.add_reaction("✔")
                            await msg.add_reaction("❌")
                            try:
                                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r,u: utilis.defaultCheck(r,u, player=self.player, message=msg), timeout=60*2)
                                if str(reaction.emoji) == "✔":
                                    await self.player.load(self.bot)
                                    activity = PlayerActivity(self.player.info['activity'])
                                    if activity == PlayerActivity.WAIT:
                                        self.player.money += price
                                        await self.player.save(self.bot)
                                        await self.player.RemoveOfCoffre(self.bot, [obj])
                                        await self.message.delete()
                                        await self.load()
                                    else:
                                        error = True
                                        content_error = "Tu es acutellement entrain de faire une activitée, attends la fin de celle-ci pour acheter ou vendre des objets."
                            except asyncio.TimeoutError:
                                pass
                            finally:
                                if error:
                                    await msg.edit(content = msg.content + f"\n**{content_error}**")
                                    await msg.clear_reactions()
                                    await asyncio.sleep(15)
                                await msg.delete()
                    elif command == "close":
                        run = False
                        await self.message.delete()
            except asyncio.TimeoutError:
                pass


    async def load(self, **kwargs):
        await self.player.load(self.bot)
        self.seller = Seller((self.player.pos_x, self.player.pos_y))
        seller_exist = await self.seller.load(self.bot)
        self.coffre = await self.player.GetCoffre(self.bot)
        if not seller_exist:
            return False
        im = self.get_gfx()
        with BytesIO() as image_binary:
            im.save(image_binary, format='PNG')
            image_binary.seek(0)
            self.message = await self.ctx.send(file=discord.File(fp=image_binary, filename='s.png'))
        return True

    def __init__(self, bot, ctx):
        super().__init__(bot, ctx)
        self.seller = None
        self.player = Player(ctx.author.id)
        self.message = None
        self.past_commands= []

    def get_gfx(self):
        begin_coffre_pos = (144, 47)
        begin_seller_pos = (15, 60)
        base_path = "images/seller_preset.png"
        seller_gfx = utilis.resize_image(self.seller.get_gfx(), 2*170)
        coffre_gfx = utilis.GetCoffreGfx(self.coffre, money=self.player.money)
        im = Image.open(base_path)
        im.paste(coffre_gfx, begin_coffre_pos, coffre_gfx)
        im = utilis.resize_image(im, 550)
        im.paste(seller_gfx, begin_seller_pos, seller_gfx)

        return im
