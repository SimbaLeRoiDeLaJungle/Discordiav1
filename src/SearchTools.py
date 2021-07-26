import random

from src.GameObject.BasicObject import BasicObject
from src.GameObject.Consumable import Consumable
from src.GameObject.Equipment import Equipment
from src.GameObject.Map import SquareType

async def GetObjectsFromSearch(bot, player, time_of_search):
    search_pos = (player.pos_x, player.pos_y)
    async with bot.pool.acquire() as conn:
        async with conn.cursor() as cursor:
            req = f"SELECT resources_type FROM worldmap_resources WHERE pos_x={search_pos[0]} AND pos_y={search_pos[1]}"
            await cursor.execute(req)
            data = await cursor.fetchone()
            await cursor.close()
            conn.close()
    type_int = 0
    if data is not None:
        type_int = data[0]

    square_type = SquareType(type_int)
    j = random.choice(range(3,5))*time_of_search/10
    obj_num = int(j)
    objs_name_specimens = GetObjectsTypeNameBySquareType(square_type)
    objs = []
    for i in range(0, obj_num):
        type = random.randint(0, 100)
        if type < 15:
            name = random.choices(objs_name_specimens['equipments'][0], objs_name_specimens['equipments'][1])
            eqp = await Equipment.GetSpecimen(bot, name[0])
            if eqp.finition_posible:
                eqp.Finition(forger_level=random.randint(0,4), fight_comp={'attaque':random.randint(0,3),'defense': random.randint(0, 3),'esquive': random.randint(0,3),'vitesse': random.randint(0,3)})
            objs.append(eqp)
        elif type < 55:
            name = random.choices(objs_name_specimens['consumable'][0],  objs_name_specimens['consumable'][1])
            cons = Consumable(name[0])
            objs.append(cons)
        else:
            name = random.choices(objs_name_specimens['basic_obj'][0], objs_name_specimens['basic_obj'][1])
            obj = BasicObject(name[0])
            objs.append(obj)
    return objs

def GetObjectsTypeNameBySquareType(square_type):
    if square_type == SquareType.PLAIN:
        return {'equipments': (['saber', 'wood-shield', 'metal-bascinet', 'brown-leather', 'black-toge', 'red-elegante-robe'],[1,3,1,2,4,4]),
                'basic_obj': (['bones', 'book', 'peau'], [3 , 2 , 1]),
                'consumable': (['champ_rouge', 'pomme_de_terre'], [1, 1])
                }
    elif square_type == SquareType.ROCK:
        return {'equipments': (['saber', 'wood-shield', 'metal-bascinet', 'brown-leather'], [1, 3, 1, 2]),
                'basic_obj': (['bones', 'book', 'branche-bois', 'peau', 'blue-cristaux'], [4 , 3, 5, 3, 1]),
                'consumable': (['champ_rouge', 'pomme_de_terre', 'viande', 'plante_1'], [3, 3, 2, 1])
                }
    elif square_type == SquareType.METAL:
        return {'equipments':(['saber', 'wood-shield', 'metal-bascinet', 'brown-leather'], [1, 3, 1, 2]),
                'basic_obj': (['bones', 'book', 'branche-bois', 'peau','yellow-cristaux'], [4, 3, 4, 3, 1]),
                'consumable': (['champ_rouge', 'pomme_de_terre'], [1,1])
                }
    elif square_type == SquareType.WOOD:
        return {'equipments': (['saber', 'wood-shield', 'metal-bascinet', 'brown-leather'], [1, 3, 1, 2]),
                'basic_obj': (['bones', 'book', 'branche-bois', 'peau', 'green-cristaux'], [4, 2, 4, 3, 1]),
                'consumable': (['champ_rouge', 'pomme_de_terre','viande'], [4, 4, 2])
                }

