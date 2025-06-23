
import sys
import json
from typing import Any, Optional



def loadJsonData(filename: str) -> Optional[Any]:
    """From Chatgpt: Charge un fichier JSON et retourne son contenu sous forme de dictionnaire ou de liste."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)  # Peut être un dict ou une liste selon le JSON
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{filename}' est introuvable.")
    except json.JSONDecodeError:
        print(f"Erreur : Le fichier '{filename}' n'est pas un JSON valide.")
    return None  # Retourne None en cas d'erreur

def convertItemsToNewFormat(itemData: dict ) -> list:
    itemsOnly = itemsData['items']['I.u']
    newListItems = list()
    for elt in itemsOnly:
        #print(f"{elt}")
        newElt = {'id':elt['id']}
        for k,v in elt['value'].items():
            # les infos viennent de dofus/datacenter/item.as
            match k:
                case 'p':
                    newElt['price'] = v
                case 'w':
                    newElt['weight'] = v
                case 'l':
                    newElt['level'] = v
                case 'g':
                    newElt['gfxid'] = v
                case 'd':
                    newElt['description'] = v
                case 't':
                    newElt['type'] = v
                case 'n':
                    newElt['name'] = v
                case 'u':
                    newElt['canuse'] = v
                case 'ut':
                    newElt['usetarget'] = v  
                case 'm':
                    newElt['iscursed'] = v
                case 'et':
                    newElt['isethereal'] = v
                case 's':
                    newElt['set'] = v
                case 'c':
                    newElt['conditions'] = v
                case 'an':
                    newElt['animation'] = v
                case 'e':
                    # TODO parser les conditions, passer d'un tableau à un dictionnaire {'':''}
                    effects = {'criticalhitbonus':v[0], 'apcost':v[1],'rangemin':v[2],'rangemax':v[3],'criticalhit':v[4],'criticalfailure':v[5],'lineonly':v[6],'lineofsight':v[7]}
                    newElt['effects'] = effects
                case 'tw':
                    # 1.12+? two hands
                    newElt['twohands'] = v
                case 'h':
                    # 1.12+? Item "caché?"
                    newElt['ishidden'] = v

                case _:
                    print(f"unknown element {k} {v} - {elt['id']}")

        newListItems.append(newElt)
    return newListItems

if __name__ == '__main__':

    itemsData = loadJsonData("output/items_fr_13.json")
    if itemsData is None:
        sys.exit(0)
    
    newData = convertItemsToNewFormat(itemsData)
    #print(f"{newData}")




    # charge le json des itemstats et le fusionne avec les items
    itemstatsdata = loadJsonData("output/itemstats_fr_1010.json")
    if itemstatsdata is None:
        sys.exit(0)

    for i,item in enumerate(newData):
        for itemstats in itemstatsdata['itemstats']['ISTA']:
            if item['id'] == itemstats['id']:
                newData[i]['stats'] = itemstats['value']
                break

    with open("items.json", "w") as outfile:
        json.dump(newData, outfile, indent=2, ensure_ascii=False)