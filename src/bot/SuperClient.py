from discord.ext.commands import Bot
import aiomysql
import src.private as private

class SuperClient(Bot):
    def __init__(self):
        super().__init__(command_prefix="!", help_command=None)
        self.pool = None

    async def launch(self):
        self.pool = await aiomysql.create_pool(host='localhost', user='disca', password=private.dbmp, db='discordia', loop=self.loop)
        self.load_extension('cog.Updater')
        self.load_extension('cog.Launcher')

