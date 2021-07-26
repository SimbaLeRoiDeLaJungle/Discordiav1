from src.GameObject.GameObject import VirtualGameObject
import src.Utilitary as utilis
from PIL import Image


class Consumable(VirtualGameObject):
    def get_gfx(self, **kwargs):
        path = utilis.consname_to_path(self.cons_type)
        im = Image.open(path)
        return im

    def __init__(self, cons_type):
        super().__init__()
        self.cons_type = cons_type
        self.name = GetConsumableNameByType(self.cons_type)
        self.price = GetPrice(cons_type)


consumable_object = [('champ_rouge', 0), ('plante_1', 2), ('pomme_de_terre', 1), ('viande', 2)]


def GetConsumableNameByType(cons_type):
    if cons_type == "champ_rouge":
        return "champignons"
    elif cons_type == "plante_1":
        return "plante médicinale"
    elif cons_type == "pomme_de_terre":
        return "pomme de terre"
    elif cons_type == "viande":
        return "viande"
    else:
        return cons_type
def GetPrice(cons_type):
    if cons_type in ['potion_bleu', 'potion_rouge','potion_orange', 'potion_vert', 'potion_jaune']:
        return 150
    elif cons_type == 'viande':
        return 15
    elif cons_type == 'plante_1':
        return 30
    elif cons_type == 'pomme_de_terre':
        return 10
    else:
        return 10
"""
async def UseConsumable(bot, player_id, consumable):
    name = consumable.cons_type
    info = await Player.GetActivity(bot, player_id)
    coffre = await Player.GetCoffre(bot, player_id)
    if coffre['consumable'][name]==0:
        return False

    if name.starswith('potion'):
        color = name[len('potion_'):]
        maladie = info.get('maladie')
        if maladie is not None:
            if maladie['color'] == color:
                info['maladie']= None
                coffre['consumable'][name] -= 1
                await Player.SetCoffre(bot, player_id, coffre)
                return "Tu as utilisé le bon remède, tu es guéris !"
        else :
            return
    elif name == 'viande':
        pass
    elif name == 'pomme_de_terre':
        pass
    elif name == 'plante_1':
        pass
    else:
        return None
"""
