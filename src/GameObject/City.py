import json

from PIL import Image

from src.GameObject.Building import BuildingType, Building
from src.GameObject.GameObject import GameObject
import random


class City(GameObject):
    async def load(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT pos_x, pos_y, king_id, city_name, resource_info, works, link FROM guilds WHERE guild_id={self.guild_id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        self.pos_x = data[0]
        self.pos_y = data[1]
        self.king_id = data[2]
        self.name = data[3]
        self.resource_info = json.loads(data[4])
        self.works = json.loads(data[5])
        self.invite_link = data[6]
        self.buildings = list()
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT building_id FROM buildings WHERE guild_id={self.guild_id}"
                await cursor.execute(req)
                data = await cursor.fetchall()
                await cursor.close()
                conn.close()
        for d in data:
            building = Building(building_id=d[0])
            await building.load(bot)
            self.buildings.append(building)

    async def save(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE guilds SET pos_x={self.pos_x}, pos_y={self.pos_y}, king_id={self.king_id}, city_name='{self.name}', resource_info=%s, works=%s, link='{self.invite_link}' WHERE guild_id={self.guild_id}"
                par = (json.dumps(self.resource_info), json.dumps(self.works))
                await cursor.execute(req, par)
                await conn.commit()
                await cursor.close()
                conn.close()

    async def store(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"INSERT INTO guilds(guild_id, pos_x, pos_y, king_id, city_name, resource_info, works, link) VALUES({self.guild_id},{self.pos_x}, {self.pos_y}, {self.king_id}, '{self.name}',%s,%s,'{self.invite_link}')"
                empty_json = json.dumps(dict())
                await cursor.execute(req, (json.dumps(self.resource_info), empty_json))
                await conn.commit()
                await cursor.close()
                conn.close()


    def get_gfx(self, **kwargs):
        background_path = "images/buildings/background.png"
        squareSize = 50
        begin_pos = (49,49)

        result = Image.open(background_path)
        for building in self.buildings:
            position = (building.city_position[0]*squareSize, building.city_position[1]*squareSize)
            print(building.building_type)
            gfx = building.get_gfx()
            w, h = gfx.size
            dx = -int((w - squareSize) / 2)
            dy = -int((h - squareSize))
            result.paste(gfx, (begin_pos[0]+dx+position[0],begin_pos[1]+dy+position[1]), gfx)
        return result

    def __init__(self, guild_id):
        super().__init__()
        self.pos_x = None
        self.pos_y = None
        self.king_id = None
        self.name = None
        self.guild_id = guild_id
        self.resource_info = {'wood':0, 'rock':0, 'metal':0, 'money':0, 'food':0}
        self.works = dict()
        self.techs = None
        self.buildings = []

    async def find_place(self, bot, width, height):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                end = False
                while not end:
                    x = random.randint(0, width - 1)
                    y = random.randint(0, height - 1)
                    dr = 4
                    conditions1 = f"pos_x={x} AND pos_y={y}"
                    conditions2 = f"pos_x<{x - dr} AND pos_x>{x + dr} AND pos_y<{y - dr} AND pos_y>{y + dr}"
                    req = f"SELECT pos_x, pos_y, resources_type FROM worldmap_resources WHERE {conditions1}"
                    await cursor.execute(req)
                    data = await cursor.fetchone()
                    if data is None:
                        req = f"SELECT pos_x, pos_y FROM guilds WHERE {conditions2}"
                        await cursor.execute(req)
                        datas = await cursor.fetchall()
                        if len(datas) == 0:
                            end = True
                            self.pos_x = x
                            self.pos_y = y
                await cursor.close()
                conn.close()

    def init_setup(self, ctx, invite_link):
        self.king_id = ctx.guild.owner_id
        self.name = ctx.guild.name
        self.invite_link = invite_link

    @staticmethod
    async def GetCityByPosition(bot, position):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT guild_id FROM guilds WHERE pos_x={position[0]} AND pos_y={position[1]}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is not None:
            city = City(data[0])
            await city.load(bot)
            return city

    @property
    def position(self):
        return self.pos_x, self.pos_y

    async def AddBuilding(self, bot, building_type, city_pos):
        if city_pos in [b.city_position for b in self.buildings]:
            return None
        else:
            cost = BuildingType.GetBuildingCost(building_type)
            if self.Paid(cost):
                building = Building(building_type=building_type, guild_id=self.guild_id)
                building.city_position = city_pos
                await building.store(bot)
                self.buildings.append(building)
                await self.save(bot)
                return building
            else:
                return None

    def Paid(self, cost):
        n_info = self.resource_info
        for key,value in cost.items():
            print(self.resource_info)
            print(cost[key])
            if self.resource_info[key] < cost[key]:
                return False
            n_info[key] -= value
        self.resource_info = n_info
        return True

    def AddWork(self,workType, work_info):
        if self.works.get(workType) is None:
            self.works[workType] = [work_info]
        else:
            self.works[workType].append(work_info)