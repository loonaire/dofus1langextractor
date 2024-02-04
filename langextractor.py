from swf.scriptextractor import extractScriptFromFile 
from dofuslang.langparser import scriptToJson
import os
import sys
import argparse


def extractAllFilesFromPath(inputDir: str,outputDir: str ,displayOutput: bool):
    for filename in os.listdir(inputDir):
        if filename.endswith('.swf'):
            script = extractScriptFromFile(inputDir + filename)
            finalJson = scriptToJson(filename, script)

            if finalJson != '':
                if not displayOutput:
                    with open(outputDir + filename.replace('.swf','.json'), 'w', encoding='utf-8') as f:
                        f.write(finalJson)
                else:
                    print(f"{finalJson}")

def extractXtraFile(inputFile: str, outputDir: str, displayOutput: bool):
    langTypeList = ['alignment', 'crafts','dialog','effects','emotes','guilds','hints','houses','interactiveobjects','items','itemsets','jobs','maps','monsters','names','npc','pvp','quests','ranks','servers','shortcuts','skills','spells','states','timezones']
    
    finalJson = ''
    script = extractScriptFromFile(inputFile)
    
    for langType in langTypeList:
        finalJson += scriptToJson(langType, script)
    
    if not displayOutput:
        with open(outputDir+ inputFile.replace('.swf','.json'), 'w', encoding='utf-8') as f:
            f.write(finalJson)
    else:
        print(f"{finalJson}")

    return

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog="dofuslangextractor",description="Converti les langs de dofus 1 en json")
    parser.add_argument('--cli', action='store_true', help="Affiche l\'extraction dans la console plutot que dans un fichier")
    parser.add_argument('-i','--input', action='store', help="Définis le dossier ou sont stockés les fichier, par défaut il s\'agit du dossier input")
    parser.add_argument('-o','--output', action='store', help="Définis le dossier des fichiers de sortie, cette option est inutile si le paramètres cli est utilisé, par défaut le dossier output est utilisé")
    parser.add_argument('--xtra', action='store_true', help="Permet de décompiler un fichier xtra des versions d'avant dofus 1.14")
    parser.add_argument('--xtrafile', action='store', help="Fichier XTRA à extraire, cet argument doit être utilisé avec l'argument xtra")
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
    
    if args.xtra != None and args.xtra == True:
        if args.xtrafile == None or (not os.path.isfile(args.xtrafile)):
            print("Erreur: argument xtrafile manquant ou le fichier n'existe pas", file=sys.stderr)
            sys.exit()

        extractXtraFile(args.xtrafile, outputPath, displayOutput)

    else:
        # Mode "normal", extrait tous les fichiers d'un dossier
        extractAllFilesFromPath(inputPath, outputPath, displayOutput)
