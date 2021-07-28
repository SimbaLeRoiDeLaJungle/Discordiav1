
import random
from io import BytesIO

import discord

from src.GameObject.Building import BuildingType
from src.GameObject.City import City
from src.GameObject.Consumable import Consumable
from src.GameObject.Equipment import Equipment
from src.GameObject.Map import Map
from src.GameObject.Player import Player, PlayerActivity
from src.GameObject.BasicObject import BasicObject
from src.bot.SuperClient import SuperClient
import asyncio
import src.private as private
from src.track.CityTrack import CityTrack
from src.track.ConstructTrack import ConstructTrack
from src.track.InfoTrack import InfoTrack
from src.track.MoveTrack import MoveTrack
from src.track.SearchTrack import SearchTrack
from src.track.SellerTrack import SellerTrack
from track.StartTrack import StartTrack
from track.CoffreTrack import CoffreTrack
from track.CollectTrack import CollectTrack
import src.Utilitary as utilis

bot = SuperClient()


@bot.event
async def on_ready():
    print("Discordia : I'm here bro' !")
    updater = bot.get_cog('Updater')
    updater.update_player_info.start()
    updater.update_seller.start()
    launcher = bot.get_cog('Launcher')
    await launcher.InitUserInfo()
    await launcher.InitUserTasks()



@bot.command()
async def start(ctx):
    track = StartTrack(bot, ctx)
    await track.load()
    await track.loop()


@bot.command()
async def coffre(ctx):
    track = CoffreTrack(bot, ctx)
    await track.load()
    await track.loop()


@bot.command()
async def a(ctx):
    city = City(ctx.guild.id)
    await city.load(bot)
    for key,_ in city.resource_info.items():
        city.resource_info[key] += 1000
    await city.save(bot)
    epq = await Equipment.GetSpecimen(bot, 'haute-forme')
    epq2 = await Equipment.GetSpecimen(bot, 'lance')
    epq3 = await Equipment.GetSpecimen(bot, 'axes')
    eqp4 = await Equipment.GetSpecimen(bot, 'fleau')
    await Player.AddEquipementsToCoffre(bot, ctx.author.id, [epq, epq2,epq3,eqp4])

@bot.command()
async def map(ctx, *args):
    show_coords = False
    show_city_info = False
    all_par = False
    for i in range(0, len(args)):
        if args[i] in ["coords", "-c"]:
            show_coords = True
        elif args[i] in ["info", "-i"]:
            show_city_info = True
        elif args[i] in ["all", "-a"]:
            all_par = True

    player = Player(ctx.author.id)
    await player.load(bot)
    x = player.pos_x
    y = player.pos_y
    map = Map((x - 3, y - 3), 7, 7)
    await map.load(bot)
    im = utilis.GetPlayersAndMapGfx(map, [player], show_coordinate=show_coords, show_city_info=show_city_info,
                                    all_par=all_par)
    with BytesIO() as image_binary:
        im.save(image_binary, format='PNG')
        image_binary.seek(0)
        await ctx.send(file=discord.File(fp=image_binary, filename='s.png'))


@bot.command()
async def move(ctx, *args):
    if len(args) == 1:
        if args[0] == "stop":
            player = Player(ctx.author.id)
            await player.load(bot)
            can_stop, activity = player.Can(PlayerActivity.WAIT)
            if can_stop and activity != PlayerActivity.WAIT:
                player.SetInfo(activity=PlayerActivity.WAIT)
                await player.save(bot)
                await ctx.send(f"Ton déplacement est anullé, tu te trouve actuellement dans la zone ({player.position_str}).")
            else:
                await ctx.send("Tu n'es pas entrain de te déplacé...")
        else:
            await ctx.send("une erreur dans la syntaxe")
    elif len(args) == 2:
        try:
            dest = (int(args[0]), int(args[1]))
            p = True
        except Exception as e:
            await ctx.send("une erreur dans la syntaxe")
            p = False

        if p:
            track = MoveTrack(bot, ctx, dest)
            await track.load()
            await track.loop()

    else:
        await ctx.send("une erreur dans la syntaxe")


@bot.command()
async def search(ctx, *args):
    if len(args) == 2:
        try:
            pos = (int(args[0]), int(args[1]))
        except Exception as e:
            pos = None
    else:
        pos = None
    track = SearchTrack(bot, ctx)
    await track.load(pos=pos)
    await track.loop()


@bot.command()
async def info(ctx):
    track = InfoTrack(bot, ctx)
    await track.load()


@bot.command()
async def seller(ctx):
    track = SellerTrack(bot, ctx)
    is_seller_exist = await track.load()
    if is_seller_exist:
        await track.loop()

@bot.command()
async def collect(ctx, *args):
    if len(args) == 0:
        track = CollectTrack(bot, ctx)
        can_loop = await track.load()
        if can_loop:
            await track.loop()
    elif len(args) == 1:
        if args[0] == 'stop':
            player = Player(ctx.author.id)
            await player.load(bot)
            if player.info['activity'] == int(PlayerActivity.COLLECT):
                player.SetInfo(activity=PlayerActivity.WAIT)
                await player.save(bot)
                await ctx.send(f"{player.mention()}, tu a arreter de collecter des resources.")
            else:
                await ctx.send(f"{player.mention()}, tu n'es pas entrain de collecter des resources...")
    else:
        pass


@bot.command()
async def createCity(ctx):
    city = City(ctx.guild.id)
    link = await ctx.channel.create_invite(max_age=0)
    city.init_setup(ctx, link.url)
    await city.find_place(bot, 100, 100)
    await city.store(bot)

@bot.command()
async def city(ctx):
    track = CityTrack(bot, ctx)
    await track.load()
    await track.loop()

@bot.command()
async def construct(ctx, *args):
    if len(args) == 3:
        try:
            b_type_str = args[0]
            city_pos = (int(args[1]), int(args[2]))
            b_type = BuildingType.StrToType(b_type_str)

        except Exception as e:
            print(e)
            await ctx.send(f"{ctx.author.mention()}, tu as commis une erreure de syntaxe.")
        else:
            if b_type is not None:
                track = ConstructTrack(bot, ctx, b_type, city_pos)
                is_running = await track.load()
                if is_running:
                    await track.loop()
                else:
                    print(is_running)
    else:
        await ctx.send(f"{ctx.author.mention()}, tu as commis une erreure de syntaxe.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.launch())
    bot.run(private.token)
