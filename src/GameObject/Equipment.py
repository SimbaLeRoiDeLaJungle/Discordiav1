import json
import random

from PIL import Image

from src.ForgeTools import GetDictForgeByObject
from src.GameObject.GameObject import GameObject
import src.Utilitary as utilis


class Equipment(GameObject):
    eqp_list_name = ['wood_shield', 'saber', 'black-toge']
    async def load(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT comp, fight_comp, name, type, sex, max_upgrade, upgrade FROM equipments WHERE obj_id={self.id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is None:
            return False
        else:
            self.comp = json.loads(data[0])
            self.fight_comp = json.loads(data[1])
            self.dbName = data[2]
            self.name = GetEquipementNameByDBName(self.dbName)
            self.type = data[3]
            self.sex = data[4]
            self.max_upgrade = data[5]
            self.upgrade = data[6]

    async def save(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE equipments SET comp=%s, fight_comp=%s, name={self.dbName}, type={self.type}, sex=%s, max_upgrade={self.max_upgrade}, upgrade={self.upgrade} WHERE obj_id={self.id}"
                par = (json.dumps(self.comp), json.dumps(self.fight_comp), self.sex)
                await cursor.execute(req, par)
                await conn.commit()
                await cursor.close()
                conn.close()

    async def store(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"INSERT INTO equipments(user_id, comp, fight_comp, name, type, sex, max_upgrade, upgrade) VALUES({self.user_id}, %s, %s, '{self.dbName}', '{self.type}',%s, {self.max_upgrade}, {self.upgrade})"
                compj = json.dumps(self.comp)
                fightcompj = json.dumps(self.fight_comp)
                await cursor.execute(req, (compj, fightcompj, self.sex))
                self.id = cursor.lastrowid
                await conn.commit()
                await cursor.close()
                conn.close()

    def get_gfx(self, **kwargs):
        kwargsex = kwargs.get('sex')
        crop = kwargs.get('crop')
        sex = "homme"
        if kwargsex is not None:
            sex = kwargsex
        elif self.sex is not None:
            sex = self.sex
        path = utilis.eqpname_to_path(self.dbName, self.type, sex)
        im = Image.open(path)
        if crop is not None:
            area = (0, 0, 64, 64)
            if self.type == 'tenue':
                area = (14, 30, 48, 60)
            elif self.type == 'torso' or self.type == 'armor':
                area = (16, 26, 50, 57)
            elif self.type == 'rhand':
                area =(3,28,32,64)
            elif self.type == 'lhand':
                area = (23, 41, 50, 60)
            elif self.type == 'legs':
                area = (21, 40, 47, 60)
            im = im.crop(area)

        return im

    def __init__(self, name=None, object_id=None, user_id=None):
        super().__init__()
        self.id = object_id
        self.user_id = user_id
        self.comp = {"medecine": 0, "recherche": 0, "bucherons": 0, "mineur": 0, "forgeron": 0, "constructeur": 0,
                     "movement": 0,
                     "craft": 0}
        self.fight_comp = {"attaque": 0, "defense": 0, "esquive": 0, "vitesse": 0}
        self.type = None
        self.sex = None
        self.dbName = name
        self.name = GetEquipementNameByDBName(name)
        self.max_upgrade = 0
        self.upgrade = 0
        self.finition_done = False
        self.price = GetPriceByDbName(self.dbName)
        self.finition_posible = False

    @staticmethod
    async def FindWithId(bot, eqp_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT user_id, comp, fight_comp, name, type, sex FROM equipments WHERE obj_id = {eqp_id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                if data is not None:
                    eqp = Equipment(object_id=eqp_id, user_id=data[0])
                    eqp.comp = json.loads(data[1])
                    eqp.fight_comp = json.loads(data[2])
                    eqp.dbName = data[3]
                    eqp.name = GetEquipementNameByDBName(data[3])
                    eqp.type = data[4]
                    eqp.sex = data[5]
                await cursor.close()
                conn.close()
        if data is None:
            return None
        return eqp

    @staticmethod
    async def GetSpecimen(bot, specimen_name):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT comp, fight_comp, type, sex, finition_possible FROM equipments_specimens WHERE name=%s"
                await cursor.execute(req, specimen_name)
                data = await cursor.fetchone()
                if data is None:
                    await cursor.close()
                    conn.close()
                    return None
                specimen = Equipment()
                if data[0] is not None:
                    specimen.comp = json.loads(data[0])
                if data[1] is not None:
                    specimen.fight_comp = json.loads(data[1])
                specimen.dbName = specimen_name
                specimen.name = GetEquipementNameByDBName(specimen_name)
                specimen.type = data[2]
                specimen.sex = data[3]
                specimen.finition_possible = data[4]
                await cursor.close()
                conn.close()
        return specimen
    def GetBasicPrice(self):
        return int(self.price + 2**(self.max_upgrade/2)*1000/2**5)
    def Finition(self, objs=None, forger=None, forger_level = None, fight_comp=None, rand_coef=None, max_upgrade=None):
        if rand_coef is None:
            rand_coef = random.randint(1,5)
        elif rand_coef > 5:
            rand_coef = 5
        elif rand_coef<1:
            rand_coef = 1
        if forger is None:
            player_coef = (forger_level+1)*rand_coef
        else:
            player_coef = (forger.comp['forge']+1)*rand_coef
        if objs is None:
            dictComp = fight_comp
        else:
            dictComp = GetDictForgeByObject(objs)
        max_player_coef = 8*5
        for key, value in dictComp.items():
            if self.fight_comp.get(key) is None:
                self.fight_comp[key] = value*player_coef
            else:
                self.fight_comp[key] += value*player_coef
        if max_upgrade is None:
            self.max_upgrade = int((player_coef+1)*10/(max_player_coef+1))
        else:
            if max_upgrade>10:
                max_upgrade = 10
            elif max_upgrade<0:
                max_upgrade =0
            self.max_upgrade = max_upgrade
        self.finition_done = True
        return player_coef / max_player_coef, dictComp


def GetEquipementNameByDBName(dbName):
    return dbName

def GetPriceByDbName(dbName):
    if dbName in ['saber', 'wood-shield']:
        return 325
    elif dbName in ['barbuta']:
        return 250
    else:
        return 100