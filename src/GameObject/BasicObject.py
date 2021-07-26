from src.GameObject.GameObject import VirtualGameObject
from PIL import Image


class BasicObject(VirtualGameObject):
    def get_gfx(self, **kwargs):
        path = f"images/basic/{self.type}.png"
        im = Image.open(path)
        return im

    def __init__(self, bo_type):
        super().__init__()
        self.type = bo_type
        self.name = GetNameByBasicObjectType(bo_type)
        self.price = GetPrice(self.type)

def GetNameByBasicObjectType(bo_type):
    if bo_type == 'blue-cristaux':
        return 'cristaux bleu'
    elif bo_type == 'bones':
        return 'os'
    elif bo_type == 'book':
        return 'livre'
    elif bo_type == 'branche-bois':
        return 'bout de bois'
    elif bo_type == 'green-cristaux':
        return 'cristaux vert'
    elif bo_type == 'peau':
        return 'peau'
    elif bo_type == 'yellow-cristaux':
        return 'cristaux jaune'
    else:
        return bo_type

def GetPrice(bo_type):
    if bo_type in ['blue-cristaux','green-cristaux','yellow-cristaux']:
        return 200
    elif bo_type == 'bones':
        return 40
    elif bo_type == 'book':
        return 5
    elif bo_type == 'branche-bois':
        return 3
    elif bo_type == 'peau':
        return 20
    else:
        return 3


basic_object_list = [('blue-cristaux', 4), ('bones', 0), ('book', 0), ('branche-bois', 0), ('green-cristaux', 4), ('peau', 1), ('yellow-cristaux', 4)]