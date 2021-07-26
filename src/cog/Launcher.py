from discord.ext import commands
from src.GameObject.Player import PlayerActivity, Player
import src.Utilitary as utilis
from datetime import timedelta, datetime


class Launcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def InitUserTasks(self):
        print("Launcher.InitUserTasks ==> begin")
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = "DELETE FROM tasks"
                await cursor.execute(req)
                await conn.commit()
                await cursor.close()
                conn.close()
        print("Launcher.InitUserTasks ==> end")

    async def InitUserInfo(self):
        print("Launcher.InitUserInfo ==> begin")
        async with self.bot.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                req = "SELECT user_id FROM users"
                print(req)
                await cursor.execute(req)
                print('execute')
                data = await cursor.fetchall()
                print(data)
                await cursor.close()
                conn.close()
        for d in data:
            player = Player(d[0])
            await player.load(self.bot)
            activity = player.info['activity']
            now = datetime.now()
            if activity == int(PlayerActivity.MOVE) or activity == int(PlayerActivity.MOVETOSEARCH):
                next_square_time = utilis.formatStrToDate(player.info['next_square_time'])
                delta = now - next_square_time
                while delta.total_seconds()>0:
                    arrived = player.PassToNextSquare()
                    if arrived:
                        print(player.id)
                        user = await self.bot.fetch_user(player.id)
                        print("user find")
                        if player.info['activity'] == int(PlayerActivity.SEARCH):
                            await user.send(f"Tu es arrivé a destination, tu commence a chercher des objets dans la zone ({player.pos_x}, {player.pos_y}), pendant {player.info['time_to_search']} minutes")
                        else:
                            await user.send("Tu es arrivé à destination")
                        break
                    else:
                        next_square_time = utilis.formatStrToDate(player.info['next_square_time'])
                        delta = now - next_square_time
                await player.save(self.bot)
        print("Launcher.InitUserInfo ==> end")


def setup(bot):
    bot.add_cog(Launcher(bot))
