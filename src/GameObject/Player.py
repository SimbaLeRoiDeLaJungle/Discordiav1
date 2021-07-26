import json
import random
from enum import IntEnum
from datetime import datetime, timedelta
from PIL import Image

from src.GameObject.BasicObject import BasicObject
from src.GameObject.GameObject import GameObject
import src.Utilitary as utilis
from src.GameObject.Consumable import Consumable
from src.GameObject.Equipment import Equipment


# noinspection PyTypeChecker
class Player(GameObject):

    async def load(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT user_id, guild_id, money, life, pos_x, pos_y, info, comp, equipments, sex, fight_comp FROM users WHERE user_id={self.id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                self.id = data[0]
                self.guild_id = data[1]
                self.money = data[2]
                self.life = data[3]
                self.pos_x = data[4]
                self.pos_y = data[5]
                self.info = json.loads(data[6])
                self.comp = json.loads(data[7])
                self.equipments = await utilis.json_to_equipments(bot, data[8])
                self.sex = data[9]
                self.fight_comp = json.loads(data[10])
                await cursor.close()
                conn.close()

    async def save(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE users SET user_id={self.id}, guild_id={self.guild_id}, money={self.money}, life={self.life}, pos_x={self.pos_x}, pos_y={self.pos_y}, info=%s, comp=%s, equipments=%s, sex={self.sex}, fight_comp=%s WHERE user_id={self.id}"
                json_info = json.dumps(self.info)
                json_comp = json.dumps(self.comp)
                json_eqp = utilis.equipments_to_json(self.equipments)
                json_fightcomp = json.dumps(self.fight_comp)
                await cursor.execute(req, (json_info, json_comp, json_eqp, json_fightcomp))
                await conn.commit()
                await cursor.close()
                conn.close()

    async def store(self, bot, **kwargs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"INSERT INTO users(user_id, guild_id, money, life, pos_x, pos_y, info, comp, equipments, sex, fight_comp) VALUES(" \
                      f"{self.id}, {self.guild_id}, {self.money}, {self.life}, {self.pos_x}, {self.pos_y}, %s, %s , %s, {self.sex}, %s)"
                info_json = json.dumps(self.info)
                comp_json = json.dumps(self.comp)
                equipments_json = utilis.equipments_to_json(self.equipments)
                fightcomp_json = json.dumps(self.fight_comp)
                await cursor.execute(req, (info_json, comp_json, equipments_json, fightcomp_json))

                req = f"INSERT INTO coffre(consumable, basic_obj, user_id) VALUES(%s,%s,{self.id}) "
                jdata = json.dumps(dict())
                await cursor.execute(req, (jdata, jdata))
                await conn.commit()
                await cursor.close()
                conn.close()

    def get_gfx(self, **kwargs):
        if self.sex:
            base_path = "images/personnages/homme/base.png"
        else:
            base_path = "images/personnages/femme/base.png"
        result = Image.open(base_path)
        hair = self.equipments['attribute']['hair']
        hair_color = self.equipments['attribute']['hair_color']
        head = self.equipments['items']['head']
        if hair is not None:
            path = utilis.eqpname_to_path(f"{hair_color}-{hair}", 'hairs', self.sex)
            im = Image.open(path)
            if head is not None:
                area = (0, 26, 64, 64)
                im = im.crop(area)
                result.paste(im, (0, 26), im)
            else:
                result.paste(im, (0, 0), im)
        tenue = self.equipments['items']['tenue']
        if tenue is not None:
            path = utilis.eqpname_to_path(tenue.name, 'tenue', self.sex)
            im = Image.open(path)
            result.paste(im, (0, 0), im)
        else:
            legs = self.equipments['items']['legs']
            if legs is not None:
                path = utilis.eqpname_to_path(legs.name, 'legs', self.sex)
                im = Image.open(path)
                result.paste(im, (0, 0), im)
            torso = self.equipments['items']['torso']
            if torso is not None:
                path = utilis.eqpname_to_path(torso.name, 'torso', self.sex)
                im = Image.open(path)
                result.paste(im, (0, 0), im)

        pads = self.equipments['items']['pads']
        if pads is not None:
            path = utilis.eqpname_to_path(pads.name, 'pads', self.sex)
            im = Image.open(path)
            result.paste(im, (0, 0), im)

        armor = self.equipments['items']['armor']
        if armor is not None:
            path = utilis.eqpname_to_path(armor.name, 'armor', self.sex)
            im = Image.open(path)
            result.paste(im, (0, 0), im)

        if head is not None:
            path = utilis.eqpname_to_path(head.name, 'head', True)
            im = Image.open(path)
            result.paste(im, (0, 0), im)
        lhand = self.equipments['items']['lhand']
        if lhand is not None:
            path = utilis.eqpname_to_path(lhand.name, 'weapon', self.sex)
            im = Image.open(path)
            result.paste(im, (0, 0), im)
        rhand = self.equipments['items']['rhand']
        if rhand is not None:
            path = utilis.eqpname_to_path(rhand.name, 'shield', True)
            im = Image.open(path)
            result.paste(im, (0, 0), im)

        return result

    def __init__(self, user_id):
        super().__init__()
        self.id = user_id
        self.guild_id = None
        self.comp = {"medecine": 0, "recherche": 0, "bucherons": 0, "mineur": 0, "forgeron": 0, "constructeur": 0,
                     "movement": 0,
                     "craft": 0}
        self.fight_comp = {"attaque": 0, "defense": 0, "esquive": 0, "vitesse": 0}
        self.life = 0
        self.money = 0
        self.guild_id = 0
        self.pos_x = -1
        self.pos_y = -1
        self.info = {'activity': PlayerActivity.WAIT}
        self.equipments = {'attribute': {'hair': None, 'hair_color': "black"},
                           'items': {'head': None, '2hands': None, 'lhand': None, 'rhand': None, 'armor': None,
                                     'tenue': None, 'torso': None, 'legs': None, 'pads': None}}
        self.sex = True

    async def is_in_db(self, bot):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT user_id FROM users WHERE user_id={self.id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                return data is not None

    def SetEquipment(self, epq):
        self.equipments['items'][epq.type] = epq
        if epq.type == 'tenue':
            self.equipments['items']['torso'] = None
            self.equipments['items']['legs'] = None
        if epq.type in ['torso', 'legs']:
            self.equipments['items']['tenue'] = None

    @staticmethod
    async def AddResourcesToCoffre(bot, player_id, wood=0, food=0, rock=0, metal=0):
        coffre_len = 200
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT wood,rock,metal,food FROM coffre WHERE user_id={player_id}"
                await cursor.execute(req)
                coffre_data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        wood_stock = coffre_data[0]
        rock_stock = coffre_data[1]
        metal_stock = coffre_data[2]
        food_stock = coffre_data[3]
        total_stock = wood_stock + rock_stock + metal_stock + food_stock
        if total_stock + wood <= coffre_len:
            total_stock += wood
            wood_stock += wood
        else:
            return False
        if total_stock + rock <= coffre_len:
            total_stock += rock
            rock_stock += rock
        else:
            return False
        if total_stock + metal <= coffre_len:
            total_stock += metal
            metal_stock += metal
        else:
            return False
        if total_stock + food <= coffre_len:
            total_stock += food
            food_stock += food
        else:
            return False
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE coffre SET wood={wood_stock}, rock={rock_stock}, food={food_stock}, metal={metal_stock} WHERE user_id={player_id}"
                await cursor.execute(req)
                await conn.commit()
                await cursor.close()
                conn.close()
        return True

    @staticmethod
    async def AddEquipementsToCoffre(bot, player_id, objs):
        max_coffre_len = 49
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT obj_id FROM equipments WHERE user_id={player_id}"
                await cursor.execute(req)
                eqp_data = await cursor.fetchall()
                req = f"SELECT consumable,basic_obj FROM coffre WHERE user_id={player_id}"
                await cursor.execute(req)
                coffre_data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        current_coffre_len = len(eqp_data)
        cons_data = json.loads(coffre_data[0])
        basicobj_data = json.loads(coffre_data[1])
        for _, value in cons_data.items():
            current_coffre_len += value
        if len(objs) + current_coffre_len > max_coffre_len:
            return False

        for obj in objs:
            if isinstance(obj, Consumable):
                if cons_data.get(obj.cons_type) is None:
                    cons_data[obj.cons_type] = 1
                else:
                    cons_data[obj.cons_type] += 1
            elif isinstance(obj, Equipment):
                obj.user_id = player_id
                await obj.store(bot)
            elif isinstance(obj, BasicObject):
                if basicobj_data.get(obj.type) is None:
                    basicobj_data[obj.type] = 1
                else:
                    basicobj_data[obj.type] += 1

        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE coffre SET consumable=%s, basic_obj=%s WHERE user_id={player_id}"
                cons_data = json.dumps(cons_data)
                basicobj_data = json.dumps(basicobj_data)
                await cursor.execute(req, (cons_data, basicobj_data))
                await conn.commit()
                await cursor.close()
                conn.close()
        return True

    async def Equip(self, bot, equip_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT * from equipments WHERE user_id={self.id} AND obj_id={equip_id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is None:
            return False
        eqp = await Equipment.FindWithId(bot, equip_id)
        self.SetEquipment(eqp)
        return True

    @staticmethod
    async def GetActivity(bot, player_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT info FROM users WHERE user_id={player_id}"
                await cursor.execute(req)
                jdata = await cursor.fetchone()
                await cursor.close()
                conn.close()
        return json.loads(jdata[0])

    @staticmethod
    async def SetActivity(bot, player_id, activity):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE users SET info=%s WHERE user_id={player_id}"
                await cursor.execute(req, json.dumps(activity))
                await conn.commit()
                await cursor.close()
                conn.close()

    async def GetCoffre(self, bot):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT consumable,basic_obj FROM coffre WHERE user_id={self.id}"
                await cursor.execute(req)
                jdata = await cursor.fetchone()
                req = f"SELECT obj_id FROM equipments WHERE user_id={self.id}"
                await cursor.execute(req)
                eqpdata = await cursor.fetchall()
                await cursor.close()
                conn.close()
        cons_data = json.loads(jdata[0])
        bo_data = json.loads(jdata[1])
        coffre = {'equipments': [], 'basic_obj': [], 'consumable': []}
        peqpid = []
        for key, value in self.equipments['items'].items():
            if value is not None:
                peqpid.append(value.id)
        for key, value in cons_data.items():
            for i in range(0, value):
                coffre['consumable'].append(Consumable(key))
        for key, value in bo_data.items():
            for i in range(0, value):
                coffre['basic_obj'].append(BasicObject(key))
        for eqp_id in eqpdata:
            if eqp_id[0] not in peqpid:
                eqp = Equipment(object_id=eqp_id[0])
                await eqp.load(bot)
                print(eqp.name)
                print(eqp.id)
                coffre['equipments'].append(eqp)
        return coffre

    def SetInfo(self, **kwargs):
        activity = kwargs.get('activity')
        dest = kwargs.get('destination')
        time_to_search = kwargs.get('time_to_search')
        square_type = kwargs.get('square_type')
        works = kwargs.get('works')
        time_to_construct = kwargs.get('time_to_construct')
        if activity == PlayerActivity.WAIT:
            if self.info['activity'] == int(PlayerActivity.MOVE):
                del self.info['next_square_time']
                del self.info['next_square']
                del self.info['destination']
                self.info['activity'] = int(activity)
            elif self.info['activity'] == PlayerActivity.SEARCH:
                del self.info['time_begin_search']
                del self.info['time_to_search']
                self.info['activity'] = int(activity)
            elif self.info['activity'] == int(PlayerActivity.MOVETOSEARCH):
                del self.info['next_square_time']
                del self.info['next_square']
                del self.info['destination']
                del self.info['time_to_search']
                self.info['activity'] = int(activity)
            elif self.info['activity'] == int(PlayerActivity.COLLECT):
                self.info['activity'] = activity
                del self.info['last_update']
                del self.info['square_type']
            if self.info['activity'] == int(PlayerActivity.CONSTRUCT):
                self.info['activity'] = activity
                del self.info['ppp']
                del self.info['building_id']
                del self.info['total_construct_point']
                del self.info['time_to_construct']
                del self.info['begin_construct_time']
                del self.info['last_update']
        if activity == PlayerActivity.MOVE and dest is not None:
            if self.info['activity'] == int(PlayerActivity.WAIT):
                self.info['activity'] = int(activity)
                self.info['next_square_time'] = utilis.formatDateToStr(
                    datetime.now() + timedelta(minutes=self.GetTimeForMoveToOneSquare()))
                self.info['next_square'] = self.GetTheBestNearSquare(dest)
                self.info['destination'] = dest
            if self.info['activity'] in [int(PlayerActivity.MOVE), int(PlayerActivity.MOVETOSEARCH)]:
                self.info['activity'] = int(activity)
                if self.info['activity'] == int(PlayerActivity.MOVETOSEARCH):
                    self.info['time_to_search'] = time_to_search
                self.info['next_square_time'] = utilis.formatDateToStr(
                    datetime.now() + timedelta(minutes=self.GetTimeForMoveToOneSquare()))
                self.info['next_square'] = self.GetTheBestNearSquare(dest)
                self.info['destination'] = dest
        if activity == PlayerActivity.SEARCH:
            if self.info['activity'] == int(PlayerActivity.WAIT):
                self.info['activity'] = int(activity)
                self.info['time_to_search'] = time_to_search
                self.info['time_begin_search'] = utilis.formatDateToStr(datetime.now())
            elif self.info['activity'] == int(PlayerActivity.MOVETOSEARCH):
                self.info['activity'] = int(activity)
                self.info['time_begin_search'] = utilis.formatDateToStr(datetime.now())
                del self.info['next_square_time']
                del self.info['next_square']
                del self.info['destination']
        if activity == PlayerActivity.MOVETOSEARCH:
            if self.info['activity'] in [int(PlayerActivity.MOVE),
                                         int(PlayerActivity.MOVETOSEARCH)] and dest is not None:
                if dest == self.info['destination']:
                    self.info['activity'] = int(activity)
                    self.info['time_to_search'] = time_to_search
            elif self.info['activity'] == int(PlayerActivity.WAIT):
                self.info['activity'] = int(activity)
                self.info['time_to_search'] = time_to_search
                self.info['next_square_time'] = utilis.formatDateToStr(
                    datetime.now() + timedelta(minutes=self.GetTimeForMoveToOneSquare()))
                self.info['next_square'] = self.GetTheBestNearSquare(dest)
                self.info['destination'] = dest
        if activity == PlayerActivity.COLLECT:
            self.info['activity'] = activity
            self.info['last_update'] = utilis.formatDateToStr(datetime.now())
            self.info['square_type'] = int(square_type)

        if activity == PlayerActivity.CONSTRUCT:
            self.info['activity'] = activity
            self.info['ppp'] = works['ppp']
            self.info['building_id'] = works['building_id']
            self.info['total_construct_point'] = 0
            self.info['time_to_construct'] = time_to_construct
            self.info['begin_construct_time'] = utilis.formatDateToStr(datetime.now())
            self.info['last_update'] = self.info['begin_construct_time']
    def GetTheBestNearSquare(self, dest):
        pos = (self.pos_x, self.pos_y)
        temp = abs(pos[0] - dest[0]) + abs(pos[1] - dest[1])
        if temp == 0:
            return pos
        nearSquares = [(pos[0] + 1, pos[1]),
                       (pos[0] - 1, pos[1]),
                       (pos[0], pos[1] + 1),
                       (pos[0], pos[1] - 1)]
        index = -1
        for i in range(0, len(nearSquares)):
            t = abs(nearSquares[i][0] - dest[0]) + abs(nearSquares[i][1] - dest[1])
            if t < temp:
                index = i
                temp = t
        return nearSquares[index]

    def GetTimeForMoveToOneSquare(self):
        return 5 * 10 / (self.comp['movement'] + 10)

    def GetConstructPointPerMinutes(self):
        return (self.comp['constructeur']+1)*0.25

    def PassToNextSquare(self):
        pos = self.info['next_square']
        self.pos_x = pos[0]
        self.pos_y = pos[1]
        dest = self.info['destination']
        temp = abs(pos[0] - dest[0]) + abs(pos[1] - dest[1])
        if temp == 0:
            if self.info['activity'] == int(PlayerActivity.MOVETOSEARCH):
                self.SetInfo(activity=PlayerActivity.SEARCH)
            else:
                self.SetInfo(activity=PlayerActivity.WAIT)
            return True
        else:
            temp_time = utilis.formatStrToDate(self.info['next_square_time'])
            self.info['next_square_time'] = utilis.formatDateToStr(
                temp_time + timedelta(minutes=self.GetTimeForMoveToOneSquare()))
            self.info['next_square'] = self.GetTheBestNearSquare(dest)
            self.info['destination'] = dest
            return False

    def Can(self, player_activity):
        current_activity = PlayerActivity(self.info['activity'])
        if current_activity in [PlayerActivity.MOVE, PlayerActivity.MOVETOSEARCH]:
            if player_activity == PlayerActivity.WAIT:
                return True, current_activity
            return False, current_activity
        elif current_activity == PlayerActivity.WAIT:
            return True, current_activity
        elif current_activity == PlayerActivity.SEARCH:
            return False, current_activity
        if current_activity == PlayerActivity.CONSTRUCT:
            return False, current_activity


    def mention(self):
        return f"<@!{self.id}>"

    @property
    def position_str(self):
        return f"{self.pos_x}, {self.pos_y}"

    @property
    def position(self):
        return self.pos_x, self.pos_y

    def estimate_time_from_distance(self):
        next_time = utilis.formatStrToDate(str(self.info['next_square_time']))
        dt = (next_time - datetime.now()).total_seconds()
        if dt < 0:
            dt = 0
        dest = self.info['destination']
        distance_in_square = abs(dest[0] - self.pos_x) + abs(dest[1] - self.pos_y)
        return (distance_in_square - 1) * self.GetTimeForMoveToOneSquare() + dt / 60

    async def RemoveOfCoffre(self, bot, objs):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT obj_id FROM equipments WHERE user_id={self.id}"
                await cursor.execute(req)
                eqp_data = await cursor.fetchall()
                req = f"SELECT consumable, basic_obj FROM coffre WHERE user_id={self.id}"
                await cursor.execute(req)
                coffre_data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        cons_info = json.loads(coffre_data[0])
        bobj_info = json.loads(coffre_data[1])
        for obj in objs:
            if isinstance(obj, Equipment):
                if obj.id in [i[0] for i in eqp_data]:
                    async with bot.pool.acquire() as conn:
                        async with conn.cursor() as cursor:
                            req = f"DELETE FROM equipments WHERE obj_id={obj.id}"
                            await cursor.execute(req)
                            await conn.commit()
                            await cursor.close()
                            conn.close()
            elif isinstance(obj, Consumable):
                if cons_info.get(obj.cons_type) is not None:
                    if cons_info.get(obj.cons_type) > 0:
                        cons_info[obj.cons_type] -= 1
                    else:
                        return False
                else:
                    return False
            elif isinstance(obj, BasicObject):
                if bobj_info.get(obj.type) is not None:
                    if bobj_info.get(obj.type) > 0:
                        bobj_info[obj.type] -= 1
                    else:
                        return False
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE coffre SET consumable=%s, basic_obj=%s WHERE user_id={self.id}"
                par = (json.dumps(cons_info), json.dumps(bobj_info))
                await cursor.execute(req, par)
                await conn.commit()
                await cursor.close()
                conn.close()

    @staticmethod
    async def AddUserTask(bot, message_id, player_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = "INSERT INTO tasks(message_id, user_id) VALUES(%s, %s)"
                await cursor.execute(req, (message_id, player_id))
                await conn.commit()
                await cursor.close()
                conn.close()

    async def DeleteUserTask(self, bot, task_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"DELETE FROM tasks WHERE message_id={task_id}"
                await cursor.execute(req)
                await conn.commit()
                await cursor.close()
                conn.close()

    async def StopAllUserTasks(self, bot):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"UPDATE tasks SET stop_task=%s WHERE user_id={self.id}"
                await cursor.execute(req, True)
                await conn.commit()
                await cursor.close()
                conn.close()

    async def AsToStopUserTask(self, bot, task_id):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT stop_task FROM tasks WHERE message_id={task_id}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await conn.commit()
                await cursor.close()
                conn.close()
        if data is None:
            return True
        else:
            return data[0]




class PlayerActivity(IntEnum):
    WAIT = 0
    MOVE = 1
    SEARCH = 2
    MOVETOSEARCH = -2
    COLLECT = 3
    CONSTRUCT = 4


def PlayerActivityToString(player_activity):
    if player_activity == PlayerActivity.WAIT:
        return "aucune"
    elif player_activity == PlayerActivity.MOVE:
        return "déplacement"
    elif player_activity == PlayerActivity.SEARCH:
        return "recherche objets"
    elif player_activity == PlayerActivity.MOVETOSEARCH:
        return "déplacement + recherche"
    elif player_activity == PlayerActivity.COLLECT:
        return "collect de ressources"
