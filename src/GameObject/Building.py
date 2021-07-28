import json
from enum import IntEnum

from PIL import Image

from src.GameObject.GameObject import GameObject

import src.Utilitary as utilis

class Building(GameObject):
    async def load(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT info, pos_x, pos_y, is_construct, building_type, guild_id FROM buildings WHERE building_id = {self.id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is not None:
            self.info = json.loads(data[0])
            self.city_position = (data[1], data[2])
            self.is_construct = data[3]
            self.building_type = BuildingType(data[4])
            self.guild_id = data[5]

    async def save(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE buildings SET info = %s, pos_x={self.city_position[0]}, pos_y={self.city_position[1]}, is_construct={self.is_construct}, building_type={self.building_type} WHERE building_id={self.id}"
                info_json = json.dumps(self.info)
                await cursor.execute(req, info_json)
                await conn.commit()
                await cursor.close()
                conn.close()

    async def store(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = "INSERT INTO buildings(guild_id,info,pos_x,pos_y,is_construct, building_type) VALUES(%s, %s, %s, %s, %s, %s)"
                info_json = json.dumps(self.info)
                await cursor.execute(req, (self.guild_id, info_json, self.city_position[0], self.city_position[1], False, int(self.building_type)))
                self.id = cursor.lastrowid
                await conn.commit()
                await cursor.close()
                conn.close()

    def get_gfx(self, **kwargs):
        if not self.is_construct:
            return Image.open("images/buildings/unConstruct.png")
        elif self.building_type == BuildingType.AUBERGE:
            return Image.open("images/buildings/auberge.png")
        elif self.building_type == BuildingType.CABINET:
            return Image.open("images/buildings/cabinet.png")
        elif self.building_type == BuildingType.CASERNE:
            return Image.open("images/buildings/caserne.png")
        elif self.building_type == BuildingType.CHAMPS:
            return Image.open("images/buildings/champs.png")
        elif self.building_type == BuildingType.COMMERCE:
            return Image.open("images/buildings/commerce.png")
        elif self.building_type == BuildingType.ELEVAGE:
            return Image.open("images/buildings/elevage.png")
        elif self.building_type == BuildingType.FORGE:
            return Image.open("images/buildings/forge.png")
        elif self.building_type == BuildingType.HABITATION:
            return Image.open("images/buildings/habitation.png")
        elif self.building_type == BuildingType.LABORATOIRE:
            return Image.open("images/buildings/laboratory.png")

    def __init__(self, guild_id=None, building_id=None, building_type=None):
        super().__init__()
        self.id = building_id
        self.building_type = building_type
        self.is_construct = False
        self.info = {'life': 0, 'max_life': 100}
        self.guild_id = guild_id
        self.city_position = None

    def construct(self, player, time_in_minutes):
        if self.is_construct:
            return True
        point_per_minutes = player.GetConstructPointPerMinutes()
        self.info['life'] += point_per_minutes * time_in_minutes
        player.info['total_construct_point'] += point_per_minutes * time_in_minutes
        if self.info['life'] >= self.info['max_life']:
            self.info['life'] = self.info['max_life']
            self.is_construct = True
            return True
        return False
    @property
    def lifeBar(self):
        return utilis.MakeLifeBar(self.info['life'], self.info['max_life'])


class BuildingType(IntEnum):
    AUBERGE = 1
    CABINET = 2
    CASERNE = 3
    CHAMPS = 4
    COMMERCE = 5
    ELEVAGE = 6
    FORGE = 7
    HABITATION = 8
    LABORATOIRE = 9
    @staticmethod
    def StrToType(string):
        if string == "auberge":
            return BuildingType.AUBERGE
        elif string == "cabinet":
            return BuildingType.CABINET
        elif string == "caserne":
            return BuildingType.CASERNE
        elif string == "champs":
            return BuildingType.CHAMPS
        elif string == "commerce":
            return BuildingType.COMMERCE
        elif string == "elevage":
            return BuildingType.ELEVAGE
        elif string == "forge":
            return BuildingType.FORGE
        elif string == "habitation":
            return BuildingType.HABITATION
        elif string == "laboratoire":
            return BuildingType.LABORATOIRE

    @staticmethod
    def TypeToStr(building_type):
        if building_type == BuildingType.AUBERGE:
            return "auberge"
        elif building_type == BuildingType.CABINET:
            return "cabinet"
        elif building_type == BuildingType.CASERNE:
            return "caserne"
        elif building_type == BuildingType.CHAMPS:
            return "champs"
        elif building_type == BuildingType.COMMERCE:
            return "commerce"
        elif building_type == BuildingType.ELEVAGE:
            return "elevage"
        elif building_type == BuildingType.FORGE:
            return "forge"
        elif building_type == BuildingType.HABITATION:
            return "habitation"
        elif building_type == BuildingType.LABORATOIRE:
            return "laboratoire"

    @staticmethod
    def GetBuildingCost(buildingType):
        if buildingType == BuildingType.AUBERGE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.CABINET:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.CASERNE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.CHAMPS:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.COMMERCE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.ELEVAGE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.FORGE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.HABITATION:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}
        elif buildingType == BuildingType.LABORATOIRE:
            return {'wood':100, 'rock':50, 'metal':50, 'money':1000}

    @staticmethod
    def TypeToStr(b_type):
        if b_type == BuildingType.AUBERGE:
            return "auberge"
        elif b_type == BuildingType.CABINET:
            return "cabinet"
        elif b_type == BuildingType.CASERNE:
            return "caserne"
        elif b_type == BuildingType.CHAMPS:
            return "champs"
        elif b_type == BuildingType.COMMERCE:
            return "commerce"
        elif b_type == BuildingType.ELEVAGE:
            return "elevage"
        elif b_type == BuildingType.FORGE:
            return "forge"
        elif b_type == BuildingType.HABITATION:
            return "habitation"
        elif b_type == BuildingType.LABORATOIRE:
            return "laboratoire"