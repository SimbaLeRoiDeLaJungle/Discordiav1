import json
from PIL import Image, ImageDraw
"""
from src.GameObject.Building import BuildingType


class CityGeneratorGfx:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        auberge_path = "images/buildings/auberge.png"
        cabinet_path = "images/buildings/cabinet.png"
        caserne_path = "images/buildings/caserne.png"
        champs_path = "images/buildings/champs.png"
        commerce_path = "images/buildings/commerce.png"
        elevage_path = "images/buildings/elevage.png"
        forge_path = "images/buildings/forge.png"
        habitation_path = "images/buildings/habitation.png"
        laboratory_path = "images/buildings/laboratory.png"
        unConstruct_path = "images/buildings/unConstruct.png"
        self.tiles_path = {BuildingType.AUBERGE: auberge_path, BuildingType.CABINET: cabinet_path,
                           BuildingType.CASERNE: caserne_path,
                           BuildingType.CHAMPS: champs_path, BuildingType.COMMERCE: commerce_path,
                           BuildingType.ELEVAGE: elevage_path,
                           BuildingType.FORGE: forge_path, BuildingType.HABITATION: habitation_path,
                           BuildingType.LABORATOIRE: laboratory_path,
                           BuildingType.UNCONSTRUCT: unConstruct_path}

    async def get_gfx(self, bot):
        tiles = dict()
        for key, value in self.tiles_path.items():
            tiles[key] = Image.open(value)

        async with bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = f"SELECT building_info FROM guilds WHERE guild_id={self.guild_id}"
                await cursor.execute(req)
                json_data = await cursor.fetchone()
                data = json.loads(json_data[0])
                background_path = "../../pythonProject/images/buildings/background.png"
                squareSize = 50
                result = Image.open(background_path)
                for d in data["items"]:
                    x = (int(d['column']) + 1) * squareSize
                    y = (int(d['line']) + 1) * squareSize
                    if d['is_construct']:
                        btype = BuildingType(d['building_type'])
                        w, h = tiles[btype].size
                        dx = -int((w-squareSize)/2)
                        dy = -int((h-squareSize))
                        result.paste(tiles[btype], (x+dx, y+dy), tiles[btype])
                    else:
                        result.paste(tiles[BuildingType.UNCONSTRUCT], (x, y))
                await cursor.close()
                conn.close()
        return result

"""