from swf.scriptextractor import extractScriptFromFile 
import re
import json
import os
import sys
import argparse

def convertMapFileToJson(filePath: str, filename: str) -> str:
    if filename.endswith('.swf'):
        script = extractScriptFromFile(filePath + filename)
        jsonStr = '{'

        for line in script.splitlines():
            if re.match('^.* = .*;$', line):
                jsonStr += '"' + line.replace(' = ', '":').replace(';', ',')
        
        jsonStr = jsonStr[:-1] + '}'

        jsonContent = dict()
        jsonContent['date'] = filename.removesuffix('.swf').split('_')[1]
        jsonContent.update(json.loads(jsonStr))

        finalJson = json.dumps(jsonContent, ensure_ascii=False, indent=2)
        return finalJson


def convertAllMapsFilesToJson(inputPath: str, outputPath: str, extractToOneFile: bool, cliMode: bool):
    mapsList = list()
    for filename in os.listdir(inputPath):
        if filename.endswith('.swf'):
            jsonExtraction = convertMapFileToJson(inputPath, filename)

            if not extractToOneFile:
                if cliMode:
                    print(f'{jsonExtraction}')
                else:
                    with open(outputPath + filename.replace('.swf','.json'), 'w', encoding='utf-8') as f:
                        f.write(jsonExtraction)
            else:
                mapsList.append(json.loads(jsonExtraction))
    if extractToOneFile:
        if not displayOutput:
            
            with open(outputPath + 'mapsextract.json','w', encoding='utf-8') as f:
                f.write(json.dumps(mapsList, ensure_ascii=False,indent=2))
        else:
            print(f"{json.dumps(mapsList, ensure_ascii=False, indent=2)}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="mapextractor",description="Converti les swf des maps de dofus 1 en json")
    parser.add_argument('--cli', action='store_true', help="Affiche l\'extraction dans la console plutot que dans un fichier")
    parser.add_argument('-i','--input', action='store', help="Définis le dossier ou sont stockés les fichier, par défaut il s\'agit du dossier input")
    parser.add_argument('-o','--output', action='store', help="Définis le dossier des fichiers de sortie, cette option est inutile si le paramètres cli est utilisé, par défaut le dossier output est utilisé")
    parser.add_argument('--singlefile', action='store_true', help='Envois le résultat dans un seul fichier json plutot que faire 1 fichier par map')
    args = parser.parse_args()

    displayOutput = True if args.cli != None and args.cli == True else False # si vrai, on affiche sur la console, sinon on envoi dans un fichier
    inputPath = args.input if args.input != None else 'input/'
    outputPath = args.output if args.output != None else 'output/'
    
    # Vérifie le dossier des fichiers d'entrées
    if len(inputPath) > 0 and inputPath[-1] != '/':
        # Si le dernier caractère du chemin n'est pas un / on le rajouter
        inputPath += '/'    
    if not os.path.exists(inputPath):
        print(f"Erreur: le chemin indiqué n'existe pas", file=sys.stderr)
        sys.exit() 

    # Vérifie le dossier des fichiers d'entrées
    if len(outputPath) > 0 and outputPath[-1] != '/':
        # Si le dernier caractère du chemin n'est pas un / on le rajouter
        outputPath += '/'    
    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    if args.singlefile != None and args.singlefile == True:
        convertAllMapsFilesToJson(inputPath, outputPath, True, displayOutput)
    else:
        convertAllMapsFilesToJson(inputPath, outputPath, False, displayOutput)

        
    pass