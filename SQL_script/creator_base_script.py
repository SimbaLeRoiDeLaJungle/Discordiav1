import pymysql
import src.private as private
import json
from src.GameObject.Map import SquareType


def getMapDictFromFile(path, max_width):
    mapDict = {SquareType.WOOD: [],
               SquareType.CITY: [],
               SquareType.PLAIN: [],
               SquareType.ROCK: [],
               SquareType.METAL: []}
    with open(path, "r") as r:
        lineIndex = 0
        line = r.readline()
        while line != '':
            print(line)
            colIndex = 0
            while colIndex < len(line) and colIndex < max_width:
                t = SquareType(int(line[colIndex]) - 1)
                mapDict[t].append((lineIndex, colIndex))
                colIndex += 1
            line = r.readline()
            lineIndex += 1
    return mapDict


torso = [('brown-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False),
         ('mail', json.dumps({'defense': 2}), json.dumps({'movement': -1}), None, True),
         ('red-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False),
         ('white-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False),
         ('white-t-shirt-long', json.dumps(dict()), json.dumps(dict()), None, False),
         ('blue-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False),
         ('pink-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False),
         ('yellow-t-shirt-normal', json.dumps(dict()), json.dumps(dict()), None, False)
         ]

legs = [('red-pants', json.dumps(dict()), json.dumps(dict()), None, False),
        ('white-pants', json.dumps(dict()), json.dumps(dict()), None, False),
        ('black-toge', json.dumps(dict()), json.dumps(dict()), True, False),
        ('blue-pants', json.dumps(dict()), json.dumps(dict()), None, False)
        ]

armor = [('blue-leather', json.dumps({'defense': 3}), json.dumps(dict()), None, True),
         ('brown-leather', json.dumps({'defense': 3}), json.dumps(dict()), None, True),
        ('brown-leather', json.dumps({'defense': 3}), json.dumps(dict()), None, True),
        ('green-leather', json.dumps({'defense': 3}), json.dumps(dict()), None, True),
         ('metal-legion', json.dumps({'defense': 4, 'attaque': 2}), json.dumps(dict()), None, True),
         ('metal-plate', json.dumps({'defense': 4, 'attaque': 2}), json.dumps(dict()), None, True)
        ]

tenue = [('red-elegante-robe', json.dumps(dict()), json.dumps(dict()), None, False),
        ('white-elegante-robe', json.dumps(dict()), json.dumps(dict()), None, False)
        ]

shield = [('wood-shield', json.dumps({'esquive': 6, 'defense': 7}), json.dumps(dict()), None, True)]
weapon =[('saber', json.dumps({'attaque': 10, 'defense': 5, 'vitesse': 5}), json.dumps(dict()), None, True)]

head =  [('barbuta', json.dumps({'defense': 5, 'attaque': 5, 'esquive': 2}), json.dumps(dict()), None, True),
         ('metal-bascinet', json.dumps({'defense': 8, 'vitesse': 5}), json.dumps(dict()), None, True),
         ('metal-head-legion', json.dumps({'defense': 8, 'attaque': 3, 'esquive': 5}), json.dumps(dict()), None, True)
        ]

conn = pymysql.Connect(host='localhost', user='disca', password=private.dbmp, db='discordia')

cursor = conn.cursor()
req = "INSERT INTO equipments_specimens(name,type,fight_comp,comp, sex, finition_possible) VALUE(%s,'{}' ,%s, %s, %s, %s)"
for eqp in torso:
    nreq = req.format('torso')
    cursor.execute(nreq, eqp)
for eqp in legs:
    nreq = req.format('legs')
    cursor.execute(nreq, eqp)
for eqp in armor:
    nreq = req.format('armor')
    cursor.execute(nreq, eqp)
for eqp in tenue:
    nreq = req.format('tenue')
    cursor.execute(nreq, eqp)
for eqp in shield:
    nreq = req.format('rhand')
    cursor.execute(nreq, eqp)
for eqp in weapon:
    nreq = req.format('lhand')
    cursor.execute(nreq, eqp)
for eqp in head:
    nreq = req.format('head')
    cursor.execute(nreq, eqp)

name = "mapTest"
path = f"../images/world.map"
mapDict = getMapDictFromFile(path, 100)
for key, value in mapDict.items():
    if key in [SquareType.METAL, SquareType.ROCK, SquareType.WOOD]:
        for square in value:
            req = f"INSERT INTO worldmap_resources(pos_x, pos_y, resources_type) VALUES({square[1]},{square[0]},{key});"
            cursor.execute(req)

conn.commit()
cursor.close()
conn.close()
print("done")
