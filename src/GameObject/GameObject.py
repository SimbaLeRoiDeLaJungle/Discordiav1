from abc import ABC, abstractmethod


class GameObject(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    async def load(self, bot, **kwargs):
        """load resources"""
        pass

    @abstractmethod
    async def save(self, bot, **kwargs):
        """save resources"""
        pass

    @abstractmethod
    async def store(self, bot, **kwargs):
        """store resources"""
        pass

    @abstractmethod
    def get_gfx(self, **kwargs):
        """get images of gameObject"""
        pass


class VirtualGameObject(ABC):
    @abstractmethod
    def get_gfx(self, **kwargs):
        pass


class SemiVirtualGameObject(ABC):
    @abstractmethod
    def get_gfx(self, **kwargs):
        pass

    @abstractmethod
    async def load(self, bot, **kwargs):
        pass
