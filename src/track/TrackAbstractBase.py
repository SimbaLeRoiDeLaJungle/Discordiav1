from abc import ABC, abstractmethod


class TrackAbstractBase(ABC):
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
    @abstractmethod
    async def loop(self):
        """main loop"""

    @abstractmethod
    async def load(self, **kwargs):
        """loading the track"""

