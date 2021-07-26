from enum import IntEnum

from PIL.ImageFont import ImageFont

from src.GameObject.GameObject import SemiVirtualGameObject

from PIL import Image, ImageDraw, ImageFont

import src.Utilitary as utilis


class Map(SemiVirtualGameObject):

    def get_gfx(self, **kwargs):
        if kwargs.get('all_par'):
            show_coordinate = True
            show_city_info = True
        else:
            show_coordinate = kwargs.get('show_coordinate')
            show_city_info = kwargs.get('show_city_info')

        tiles = dict()

        for key, path in tiles_path.items():
            tiles[key] = Image.open(path)
            tiles[key] = utilis.resize_image(tiles[key], self.squareSize)

        result = Image.new(mode="RGB", size=(self.squareSize * self.width, self.squareSize * self.height))

        line = 0
        while line != self.height:
            col = 0
            while col != self.width:
                x = col * self.squareSize
                y = line * self.squareSize
                result.paste(tiles[SquareType.PLAIN], (x, y))
                col += 1
            line += 1
        draw = ImageDraw.Draw(result)
        font = ImageFont.truetype(r"arial.ttf", 10)
        for square in self.squares:
            x = (square["pos_x"] - self.topLeft_x) * self.squareSize
            y = (square["pos_y"] - self.topLeft_y) * self.squareSize
            t = square["square_type"]
            result.paste(tiles[t], (x, y))
            if show_city_info:
                name = square["name"]
                if name is not None:
                    width, height = draw.textsize(name, font)
                    text_pos = (x + (self.squareSize - width) / 2, y + self.squareSize - height)
                    draw.text(text_pos, name, font=font, fill="red")

        line = 0
        while line != self.height:
            begin = (0, line * self.squareSize)
            end = (self.width * self.squareSize, line * self.squareSize)
            draw.line([begin, end], fill="black")
            line += 1
        col = 0
        while col != self.width:
            begin = (col * self.squareSize, 0)
            end = (col * self.squareSize, self.height * self.squareSize)
            draw.line([begin, end], fill="black")
            col += 1

        line = 0
        if show_coordinate:
            while line != self.height:
                col = 0
                while col != self.width:
                    x = (self.topLeft_x + col)
                    y = (self.topLeft_y + line)
                    draw.text((col * self.squareSize + 1, line * self.squareSize), f"X:{x}\nY:{y}", font=font, fill="white")
                    col += 1
                line += 1
        return result

    async def load(self, bot, **kwargs):
        self.squares.clear()
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                conditions = f"pos_x>={self.topLeft_x} AND pos_x<{self.topLeft_x + self.width} AND pos_y>={self.topLeft_y} AND pos_y<{self.topLeft_y + self.height}"

                req = f"SELECT pos_x, pos_y, resources_type FROM worldmap_resources WHERE {conditions}"
                await cursor.execute(req)
                datas = await cursor.fetchall()
                for data in datas:
                    self.squares.append({'pos_x': data[0], 'pos_y': data[1], 'square_type': data[2], 'name': None})

                req = f"SELECT pos_x, pos_y, city_name FROM guilds WHERE {conditions}"
                await cursor.execute(req)
                datas = await cursor.fetchall()
                for data in datas:
                    self.squares.append(
                        {'pos_x': data[0], 'pos_y': data[1], 'square_type': SquareType.CITY, 'name': data[2]})

                req = f"SELECT pos_x, pos_y FROM seller WHERE {conditions}"
                await cursor.execute(req)
                datas = await cursor.fetchall()
                for data in datas:
                    self.squares.append(
                        {'pos_x': data[0], 'pos_y': data[1], 'square_type': SquareType.SELLER, 'name': None}
                    )
                await cursor.close()
                conn.close()

    def __init__(self, topLeft_corner, width, height,squareSize=55):
        self.topLeft_x = topLeft_corner[0]
        self.topLeft_y = topLeft_corner[1]
        self.width = width
        self.height = height
        self.squares = []
        self.squareSize = squareSize

    @staticmethod
    async def GetOneSquareType(bot, pos):
        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT resources_type FROM worldmap_resources WHERE pos_x={pos[0]} AND pos_y ={pos[1]}"
                await cursor.execute(req)
                data = await cursor.fetchone()
                await cursor.close()
                conn.close()
        if data is None:
            async with bot.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    req = f"SELECT guild_id FROM guilds WHERE pos_x={pos[0]} AND pos_y={pos[1]}"
                    await cursor.execute(req)
                    data = await cursor.fetchone()
                    await cursor.close()
                    conn.close()
            if data is None:
                return 0
            else:
                return SquareType.CITY
        else:
            return data[0]


class SquareType(IntEnum):
    PLAIN = 0
    WOOD = 1
    ROCK = 2
    METAL = 3
    CITY = 4
    SELLER = 5


tiles_path = {SquareType.PLAIN: "images/map/empty_tiles.png", SquareType.WOOD: "images/map/woodTile.png",
              SquareType.ROCK: "images/map/rock_tiles.png", SquareType.METAL: "images/map/rock_tiles.png",
              SquareType.CITY: "images/map/city_tiles.png",
              SquareType.SELLER: "images/map/marchand.png"}


def GetSquareTypeStr(squareType, pre=False):
    if squareType == SquareType.WOOD:
        if pre:
            return "du bois"
        else:
            return "bois"
    elif squareType == SquareType.ROCK:
        if pre:
            return "de la pierre"
        else:
            return "pierre"
    elif squareType == SquareType.METAL:
        if pre:
            return "du métal"
        else:
            return "métal"
    elif squareType == SquareType.PLAIN:
        if pre:
            return "la plaine"
        else:
            return "plain"
    elif squareType == SquareType.CITY:
        if pre:
            return "une ville"
        else:
            return "ville"