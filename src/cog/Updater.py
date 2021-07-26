import random
from io import BytesIO

import discord
from discord.ext import commands, tasks
import json
from datetime import datetime, timedelta

from src.GameObject.Building import Building
from src.GameObject.Map import SquareType
from src.GameObject.Player import Player, PlayerActivity
from src.GameObject.Seller import GetRandomSellerInfo
from src.SearchTools import GetObjectsFromSearch
import src.Utilitary as utilis


class Updater(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=30)
    async def update_player_info(self):
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = "SELECT user_id FROM users"
                await cursor.execute(req)
                data = await cursor.fetchall()
                await cursor.close()
                conn.close()

        for d in data:
            player = Player(d[0])
            await player.load(self.bot)
            now = datetime.now()
            if player.info['activity'] in [int(PlayerActivity.MOVE), int(PlayerActivity.MOVETOSEARCH)]:
                next_square_time = utilis.formatStrToDate(player.info['next_square_time'])
                delta = next_square_time - now
                if delta.total_seconds() <= 0:
                    arrived = player.PassToNextSquare()
                    await player.save(self.bot)
                    if arrived:
                        user = await self.bot.fetch_user(player.id)
                        if player.info['activity'] == int(PlayerActivity.SEARCH):
                            await user.send(f"Tu es arrivé a destination, tu commence a chercher des objets dans la zone ({player.pos_x}, {player.pos_y}), pendant {player.info['time_to_search']} minutes")
                        else:
                            await user.send("Tu es arrivé à destination")
            elif player.info['activity'] == int(PlayerActivity.SEARCH):
                b_time = utilis.formatStrToDate(player.info['time_begin_search'])
                d_time = timedelta(minutes=player.info['time_to_search'])
                end_time = b_time + d_time
                delta = end_time-now
                if delta.total_seconds() <= 0:
                    player.SetInfo(activity=PlayerActivity.WAIT)
                    await player.save(self.bot)
                    objs = await GetObjectsFromSearch(self.bot, player, d_time.total_seconds()/60)
                    await player.AddEquipementsToCoffre(self.bot, player.id, objs)
                    user = await self.bot.fetch_user(player.id)
                    im = utilis.GetObjectsInfoGfx(objs)
                    with BytesIO() as image_binary:
                        im.save(image_binary, format='PNG')
                        image_binary.seek(0)
                        await user.send(content= "ta recherche est finie, voila ce que tu trouver :", file=discord.File(fp=image_binary, filename='s.png'))

            elif player.info['activity'] == int(PlayerActivity.COLLECT):
                last_update = utilis.formatStrToDate(player.info['last_update'])
                next_update = last_update + timedelta(seconds=30)
                delta = next_update - now
                if delta.total_seconds() < 0:
                    player.info['last_update'] = utilis.formatDateToStr(now)
                    square_type = player.info['square_type']
                    player_not_full = True
                    if square_type == SquareType.WOOD:
                        player_not_full = await Player.AddResourcesToCoffre(self.bot, player.id,wood=1)
                    elif square_type == SquareType.ROCK:
                        player_not_full = await Player.AddResourcesToCoffre(self.bot, player.id, rock=1)
                    elif square_type == SquareType.METAL:
                        player_not_full = await Player.AddResourcesToCoffre(self.bot, player.id, metal=1)
                    if not player_not_full:
                        player.SetInfo(activity=PlayerActivity.WAIT)
                        await player.save(self.bot)
                        user = await self.bot.fetch_user(player.id)
                        await user.send("Tu as finis de récolter des resources")
            elif player.info['activity'] == int(PlayerActivity.CONSTRUCT):
                last_update = utilis.formatStrToDate(player.info['last_update'])
                delta = now - last_update
                player.info['last_update'] = utilis.formatDateToStr(now)
                time_end = utilis.formatStrToDate(player.info['begin_construct_time']) + timedelta(minutes=player.info['time_to_construct'])
                building_id = player.info['building_id']
                building = Building(building_id=building_id)
                await building.load(self.bot)
                is_construct = building.construct(player, delta.total_seconds()/60)
                if is_construct or (time_end-now).total_seconds()<0:
                    salaire = round(player.info['total_construct_point']* player.info['ppp'])
                    player.money += salaire
                    player.SetInfo(activity=PlayerActivity.WAIT)
                    user = await self.bot.fetch_user(player.id)
                    if user is not None:
                        await user.send(f"Tu as fini de travailler, tu as gagner {salaire}.")
                await player.save(self.bot)
                await building.save(self.bot)

    @tasks.loop(hours=1)
    async def update_seller(self):
        map_height = 100
        map_width = 100
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:

                req = "DELETE FROM seller"
                await cursor.execute(req)

                req = "SELECT pos_x, pos_y FROM worldmap_resources"
                await cursor.execute(req)
                data = await cursor.fetchall()

                req = "SELECT pos_x, pos_y FROM guilds"
                await cursor.execute(req)
                data_city = await cursor.fetchall()
                data = list(data)
                for d in data_city:
                    data.append(d)
                for _ in range(0,20):
                    pos_x, pos_y = data[0]
                    while (pos_x, pos_y) in data:
                        pos_x, pos_y = (random.randint(0, map_width), random.randint(0, map_height))

                    req = f"INSERT INTO seller(pos_x,pos_y, info) VALUES({pos_x},{pos_y},%s)"
                    info = json.dumps(GetRandomSellerInfo())
                    await cursor.execute(req, info)

                await conn.commit()
                await cursor.close()
                conn.close()

def setup(bot):
    bot.add_cog(Updater(bot))