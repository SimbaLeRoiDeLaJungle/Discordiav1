
def GetDictForgeByObject(objs):
    fcomp = {'attaque':0, 'defense':0, 'equive':0, 'vitesse':0}
    for i in range(0, min(len(objs), 3)):
        if objs[i].bo_type == 'blue-cristaux':
            fcomp['attaque'] += 4
        elif objs[i].bo_type == 'green-cristaux':
            fcomp['defense'] += 4
        elif objs[i].bo_type == 'yellow-cristaux':
            fcomp['esquive'] += 2
            fcomp['vitesse'] += 2
        elif objs[i].bo_type in ['bones', 'peau']:
            fcomp['attaque'] += 1
            fcomp['defense'] += 1
    return fcomp

