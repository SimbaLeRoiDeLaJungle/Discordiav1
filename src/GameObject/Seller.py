import json
import random
import src.Utilitary as utilis
from src.GameObject.BasicObject import BasicObject
from src.GameObject.Consumable import Consumable
from src.GameObject.Equipment import Equipment
from src.GameObject.GameObject import SemiVirtualGameObject
from PIL import ImageDraw,ImageFont, Image

class Seller(SemiVirtualGameObject):

    def get_gfx(self, **kwargs):
        l = [eqp for eqp in self.info['equipments']]

        for obj in self.info['basic_obj']:
            l.append(obj)
        for cons in self.info['consumable']:
            l.append(cons)
        prices = [self.get_price(obj) for obj in l]
        im = utilis.GetObjectsInfoGfx(l)
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("arial.ttf", 50)
        posX = 400
        coin_gfx = utilis.resize_image(Image.open("images/coin.png"), 45)
        for i in range(0,len(prices)):
            posY = 40+i*160
            draw.text((posX, posY+2),f"{prices[i]}", font=font, fill='yellow', stroke_fill='black', stroke_width=1)
            w,_ = font.getsize(f"{prices[i]}")
            im.paste(coin_gfx, (posX+w+10, posY), coin_gfx)
        return im

    async def load(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT info FROM seller WHERE pos_x={self.pos_x} AND pos_y={self.pos_y}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is None:
            return False
        else:
            info = json.loads(data[0])
            self.info = {'equipments':[], 'basic_obj':[], 'consumable':[]}
            for eqpInfo in info['equipments']:
                eqp = await Equipment.GetSpecimen(bot, eqpInfo['dbName'])
                forger_level = eqpInfo['forger_level']
                rand_coef = eqpInfo['rand_coef']
                max_upgrade = eqpInfo['max_upgrade']
                fight_comp = eqpInfo['fight_comp']
                eqp.Finition(fight_comp=fight_comp, forger_level=forger_level, rand_coef=rand_coef, max_upgrade=max_upgrade)
                self.info['equipments'].append(eqp)
            for objname in info['basic_obj']:
                obj = BasicObject(objname)
                self.info['basic_obj'].append(obj)
            for consname in info['consumable']:
                cons = Consumable(consname)
                self.info['consumable'].append(cons)
            self.info['politique'] = info['politique']
            return True

    def __init__(self, pos):
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        self.info = dict()

    def get_price(self, obj, mode ='sell_price'):
        politique = self.info['politique'][mode]
        if politique == 'cheap':
            coef = 0.75
        elif politique == 'normal':
            coef = 1
        elif politique == 'expansive':
            coef = 1.25
        if isinstance(obj, Equipment):
            b_price = obj.GetBasicPrice()
        else:
            b_price = obj.price
        if mode == 'buy_price':
            coef= coef*0.75
        return int(b_price*coef)
    async def Exist(self, bot):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT info FROM seller WHERE pos_x={self.pos_x} AND pos_y={self.pos_y}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        return data is not None
def GetRandomSellerInfo():
    rand = random.randint(0,2)
    if rand == 0:
        return {'equipments': [{'dbName': 'saber', 'fight_comp':{'attaque': 3, 'defense': 3, 'esquive': 1, 'vitesse': 2},'max_upgrade': 4,'rand_coef': 2, 'forger_level':2},
                            {'dbName': 'wood-shield', 'fight_comp': {'attaque': 1, 'defense': 5, 'esquive': 2, 'vitesse': 2}, 'max_upgrade': 4,'rand_coef': 2, 'forger_level':2}
                            ],
             'basic_obj': ['blue-cristaux'],
             'consumable': ['viande'],
             'politique' : {'sell_price': 'cheap', 'buy_price':'cheap'}
             }
    elif rand == 1:
        return {'equipments': [{'dbName': 'barbuta', 'fight_comp':{'attaque': 1, 'defense': 4, 'esquive': 2, 'vitesse': 1},'max_upgrade': 4,'rand_coef': 3, 'forger_level':3}],
             'basic_obj': ['yellow-cristaux', 'green-cristaux'],
             'consumable': ['viande'],
             'politique' : {'sell_price': 'expansive', 'buy_price': 'normal'}
             }
    elif rand == 2:
        return {'equipments': [{'dbName': 'saber', 'fight_comp':{'attaque': 3, 'defense': 3, 'esquive': 1, 'vitesse': 2},'max_upgrade': 4,'rand_coef': 2, 'forger_level':2},
                            {'dbName': 'wood-shield', 'fight_comp': {'attaque': 1, 'defense': 5, 'esquive': 2, 'vitesse': 2}, 'max_upgrade': 4,'rand_coef': 2, 'forger_level':2}
                            ],
             'basic_obj': ['blue-cristaux'],
             'consumable': ['champ_rouge'],
             'politique' : {'sell_price': 'normal', 'buy_price':'normal'}
             }

