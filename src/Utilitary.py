import json
import random
from datetime import datetime

from src.GameObject.Equipment import Equipment
from PIL import Image, ImageFont, ImageDraw


def equipments_to_json(equip_dict):
    result = {'attribute': equip_dict['attribute'], 'items': dict()}
    for key, value in equip_dict['items'].items():
        if value is not None:
            result['items'][key] = value.id
        else:
            result['items'][key] = None
    return json.dumps(result)


async def json_to_equipments(bot, json_data):
    data = json.loads(json_data)
    eqps = {'items': dict(), 'attribute': data['attribute']}
    for key, value in data['items'].items():
        if value is not None:
            eqp = await Equipment.FindWithId(bot, value)
            eqps['items'][key] = eqp
        else:
            eqps['items'][key] = None
    return eqps


def eqpname_to_path(name, type_string, sexe):
    if type_string == 'rhand':
        sexe = True
        type_string = 'shield'
    elif type_string == 'lhand':
        type_string = 'weapon'
    if sexe:
        s = "homme"
    else:
        s = "femme"
    return f"images/personnages/{s}/{type_string}/{name}.png"


def resize_image(img, basewidth):
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    return img


def str_to_int(string):
    try:
        return int(string)
    except Exception as e:
        r = 0
        i = 1

        if ord("A") <= ord(string) <= ord("Z"):
            r = (ord(string) - ord("A"))*i

        return r


def consname_to_path(name):
    return f"images/consumable/{name}.png"


def keyToAbrev(k):
    if k == 'attaque':
        return 'ATK'
    elif k == 'defense':
        return 'DEF'
    elif k == 'vitesse':
        return 'VIT'
    elif k == 'esquive':
        return 'ESQ'
    elif k == 'movement':
        return 'DEP'
    elif k == 'bucherons':
        return 'BUCH'
    elif k == "mineur":
        return "MIN"
    elif k == "forgeron":
        return "FORG"
    elif k == "constructeur":
        return "CNST"
    elif k == "craft":
        return "CRFT"
    elif k == "medecine":
        return "MED"
    elif k == "recherche":
        return "SRCH"


def GetPlayersAndMapGfx(map_part, players, **kwargs):
    show_coords = kwargs.get('show_coordinate')
    show_city_info = kwargs.get('show_city_info')
    all_par = kwargs.get('all_par')
    im = map_part.get_gfx(show_coordinate=show_coords, show_city_info=show_city_info, all_par=all_par)
    for player in players:
        gfx = resize_image(player.get_gfx(), int(map_part.squareSize / 2))
        x = int((player.pos_x - map_part.topLeft_x) * map_part.squareSize)
        y = int((player.pos_y - map_part.topLeft_y + 1 / 2) * map_part.squareSize)
        im.paste(gfx, (x, y), gfx)
    return im


def formatStrToDate(date: str):
    return datetime.strptime(date, "%m/%d/%Y, %H:%M:%S")


def formatDateToStr(date: datetime):
    return date.strftime("%m/%d/%Y, %H:%M:%S")


def FloatSecondToStr(sec_tot):
    hours = (sec_tot // 60) // 60
    minutes = (sec_tot // 60) % 60
    seconds = (sec_tot % 60) % 60
    r = ""
    if hours != 0:
        r += f" {int(hours)}h"
    if minutes != 0:
        r += f" {int(minutes)}m"
    if seconds != 0:
        r += f" {int(seconds)}s"
    if r == "":
        return "0s"
    return r


def GetObjectsInfoGfx(objs):
    if len(objs) <= 4:
        max_line = len(objs)
        max_col = 1
    else:
        max_line = 4
        max_col = len(objs) // max_line + 1
    base_size = (360, 163)
    im = Image.new(size=((max_col + 1) * base_size[0], max_line * base_size[1]), mode="RGBA")
    line = 0
    col = 0
    base_path = "images/obj_ban.png"
    gfx_pos = (28, 22)
    gfx_size = (60, 60)
    font = ImageFont.truetype(r"arial.ttf", 25)
    font_small = ImageFont.truetype(r"arial.ttf", 15)
    name_pos = (112, 48)
    comp_pos = (16, 95)
    comp_size = (115, 20)
    for obj in objs:
        if obj is not None:
            print(obj.name)
            base = Image.open(base_path).convert("RGBA")
            gfx = resize_image(obj.get_gfx(crop=True), gfx_size[0]).convert("RGBA")
            base.paste(gfx, gfx_pos, gfx)
            draw = ImageDraw.Draw(base)
            draw.text(name_pos, obj.name, font=font, fill='black')
            x, y = (col * base_size[0], line * base_size[1])
            if isinstance(obj, Equipment):
                if obj.max_upgrade != 0:
                    draw.text(comp_pos, f"UPGRADE : {obj.upgrade}/{obj.max_upgrade}", font=font_small, fill='black')
                    intern_line = 1
                else:
                    intern_line = 0
                intern_col = 0
                max_intern_line = 3
                for key, value in obj.fight_comp.items():
                    i_x = intern_col * comp_size[0] + comp_pos[0]
                    i_y = intern_line * comp_size[1] + comp_pos[1]
                    draw.text((i_x, i_y), f"{keyToAbrev(key)}: +{value}", font=font_small, fill='black')
                    intern_line += 1
                    if intern_line >= max_intern_line:
                        intern_line = 0
                        intern_col += 1
            im.paste(base, (x, y), base)
            line += 1
            if line >= max_line:
                line = 0
                col += 1
    return im


def defaultCheck(reaction, user, emoji_list=["✔", "❌"], player=None, message=None):
    return str(reaction.emoji) in emoji_list and user.id == player.id and message.id == reaction.message.id


def GetCoffreGfx(coffre, money=None):
    item_size = (15, 15)
    padding = (1, 1)
    col = 0
    line = 0
    max_col = 7
    im_width = max_col * (item_size[0] + padding[0])
    im_height = 10*(item_size[1]+ padding[1])
    im = Image.new(mode="RGBA", size=(im_width, im_height))
    for eqp in coffre['equipments']:
        gfx = resize_image(eqp.get_gfx(crop=True), item_size[0])
        x = (padding[0] + item_size[0]) * col
        y = (padding[1] + item_size[1]) * line
        im.paste(gfx, (x, y), gfx)
        col += 1
        if col >= max_col:
            col = 0
            line += 1
    for value in coffre['consumable']:
        gfx = value.get_gfx().convert("RGBA")
        gfx = resize_image(gfx, 15)
        x = (padding[0] + item_size[0]) * col
        y = (padding[1] + item_size[1]) * line
        im.paste(gfx, (x, y), gfx)
        col += 1
        if col >= max_col:
            col = 0
            line += 1
    for value in coffre['basic_obj']:
        gfx = value.get_gfx().convert("RGBA")
        gfx = resize_image(gfx, 15)
        x = (padding[0] + item_size[0]) * col
        y = (padding[1] + item_size[1]) * line
        im.paste(gfx, (x, y), gfx)
        col += 1
        if col >= max_col:
            col = 0
            line += 1
    if money is not None:
        font = ImageFont.truetype("arial.ttf", 8)
        draw = ImageDraw.Draw(im)
        txt = f"money : {str(money)}"
        coin_gfx = resize_image(Image.open("images/coin.png"), 10)
        money_pos = (10, item_size[1]*8-2)
        w, _ = font.getsize(txt)
        draw.text(money_pos, txt, fill='yellow', font=font, stroke_width=1, stroke_fill='black')
        im.paste(coin_gfx, (money_pos[0]+w+5, money_pos[1]), coin_gfx)

    return im


def MakeLifeBar(pos , maximum, compt=6):
    e1 = "🟩"
    e2 = "🟥"
    if maximum != 0:
        d = pos / maximum
    else:
        d = 1
    bar = ""
    for i in range(0, compt):
        if i < d * compt:
            bar += e1
        else:
            bar += e2
    return bar