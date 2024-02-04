import re
import json

def addDoubleQuoteToJsonAttrName(content: str) -> str:
    attrNameList = ['n', 'c', 'g', 'm','i','v', 'l', 'd','t','o','a','e','ep','k','x','y','sa','sua','s','p', 'pt','j','io','f','cl','r','nc','nl','p1','p2','l1','l2','l3','l4','l5','l6','up','pc','b','fc','bc','rlng','date','c1','c2','c3', 'g1','g2','g3','g4','g5','g6','g7','g8','g9','g10','lp','ap','mp','z','nn','wd','fm','w','u','an','tw','ut','et','ce','sk','wm','pm', 'cm','xm', 'sm','z','b10','b11','b12','b13','b14','b15','b16','cc','pt','pc','pd','di','sd','sn','ln','av']
    for attrName in attrNameList:
        content = content.replace(f',{attrName}:', f',"{attrName}":').replace(f'{{{attrName}:', f'{{"{attrName}":') 

    # nettoie certains attributs qui ont des concat de str dans leurs chaines... (sorts vulné panda)
    content = content.replace(f'"\\"', f'\\"') # cas des vulné panda ainsi que d'autres cas dans le fichier speakingItems
    if content[0:2] == f'\\"':
        # Cas particulier où le début de la chaine commence par une double quote
        content = '"' + content
    
    # cas ou les chaines commencent pas une double quote
    content = content.replace(f'":\\"', '":"\\"')

    # HACK cas particuliers
    content = content.replace(f'\x16',f'0x16') # cas des spells avec des caractères hexa dans la description
    content = content.replace(f'\t',f'\\t')
    return content

    
def convertAllValidLineObjectToJson(fileContent: str, objectsName: list, variablesArrayName: list) -> dict:
    jsonOut = dict()

    for objectName in objectsName:
        extractedElements = list()
        for line in fileContent.splitlines():
            
            objectRegex = fr'^{objectName}\[([0-9]+|".*")\] = (\{{.*\}});$'
            validObjectLine = re.search(objectRegex, line)
            if validObjectLine != None:
                jsonContent = dict()
                jsonContent['id'] = int(validObjectLine.group(1))
                jsonContent['value'] = json.loads(addDoubleQuoteToJsonAttrName(validObjectLine.group(2)))
                extractedElements.append(jsonContent)
        jsonOut[objectName] = extractedElements

    for variableArrayName in variablesArrayName:
        extractedElements = list()

        for line in fileContent.splitlines():
            # si il n'y a aucune correspondance pour le for des objets, charge les lignes de la forme: nomVar[elt]= val
            variableRegex = fr'^{variableArrayName}\[([0-9]+|".*")\] = (.*);$'
            validVariableArrayLine = re.search(variableRegex, line)
            if validVariableArrayLine != None:
                jsonContent = dict()
                jsonContent['id'] = int(validVariableArrayLine.group(1))
                jsonContent['value'] = json.loads(addDoubleQuoteToJsonAttrName(validVariableArrayLine.group(2)))
                extractedElements.append(jsonContent)
        jsonOut[variableArrayName] = extractedElements       

    return jsonOut

def convertAllValidLineObjectWithMembrToJson(fileContent: str, objectsName: list, membersName: list) -> dict:
    jsonOut = dict()
    for objectName in objectsName:
        for memberName in membersName:
            extractedElements = list()
            for line in fileContent.splitlines():
                regexLine = fr'^{objectName}\[([0-9]+|".*")\]\.{memberName}\[([0-9]+|".*")\] = (\{{.*\}});$'
                validObjectLine = re.search(regexLine, line)
                if validObjectLine != None:
                    jsonContent = dict()
                    jsonContent['id'] = int(validObjectLine.group(1))
                    jsonContent['member'] = {'name': memberName, 'id': int(validObjectLine.group(2))}
                    jsonContent['value'] = json.loads(addDoubleQuoteToJsonAttrName(validObjectLine.group(3)))
                    extractedElements.append(jsonContent)
            jsonOut[objectName + '.' + memberName] = extractedElements
    
    return jsonOut

def convertAllValidLineVariableWithArrayObjectToJson(fileContent: str, variablesName: list) -> dict:
    # TODO si fonctionne, reprendre pour envoyer le résultat sous forme d'un seul dict plutot qu'un dict qui contient des dict(jsonContent est intégré à jsonOut) 
    jsonOut = dict()
    for variableName in variablesName:
        extractedElements = list()
        for line in fileContent.splitlines():
            regexLine = fr'^{variableName} = (\[?\{{.*\}}\]?);$'
            validLine = re.search(regexLine, line)
            if validLine != None:
                jsonContent = dict()
                jsonContent[variableName] = json.loads(addDoubleQuoteToJsonAttrName(validLine.group(1)))
                extractedElements.append(jsonContent)
        jsonOut[variableName] = extractedElements
    
    return jsonOut
   
def convertAllVariablesLinesToJson(fileContent: str, variablesName: list) -> dict:
    # TODO si fonctionne, reprendre pour envoyer le résultat sous forme d'un seul dict plutot qu'un dict qui contient des dict(jsonContent est intégré à jsonOut) 
    jsonOut = dict()

    for variableName in variablesName:
        extractedElements = list()
        for line in fileContent.splitlines():
            regexLine = fr'^{variableName} = (.*);$'
            validLine = re.search(regexLine, line)
            if validLine != None:
                    jsonContent = dict()
                    if validLine.group(1)[0] == '[' and validLine.group(1)[-1] == ']':
                        # Cas ou la valeur de la variable est un tableau
                        jsonContent['value'] = json.loads(addDoubleQuoteToJsonAttrName(validLine.group(1)))
                    else:
                        # on tente de convertir en int si il s'agit d'un int:
                        try:
                            jsonContent['value'] = int(validLine.group(1))
                        except:
                            # si ce n'est pas un int, on considère qu'il s'agit d'un str
                            jsonContent['value'] = validLine.group(1)
                    extractedElements.append(jsonContent)
        jsonOut[variableName] = extractedElements
    
    return jsonOut

def convertAllVariablesArrayOfArrayLinesToJson(fileContent: str, variablesName: list) -> list:
    jsonOut = dict()
    for variableName in variablesName:
        extractedElements = list()
        for line in fileContent.splitlines():
            regexLine = fr'^{variableName}\[([0-9]+)\]\[([0-9]+)\] = (.*);$'
            validLine = re.search(regexLine, line)
            if validLine != None:
                    jsonContent = dict()
                    jsonContent['id'] = int(validLine.group(1))
                    jsonContent['id2'] = int(validLine.group(2))
                    if validLine.group(3)[0] == '[' and validLine.group(3)[-1] == ']':
                        # Cas ou la valeur de la variable est un tableau
                        jsonContent['value'] = json.loads(addDoubleQuoteToJsonAttrName(validLine.group(3)))
                    else:
                        # on tente de convertir en int si il s'agit d'un int:
                        try:
                            jsonContent['value'] = int(validLine.group(3))
                        except:
                            jsonContent['value'] = validLine.group(3)
                    extractedElements.append(jsonContent)
        jsonOut[variableName] = extractedElements
    return jsonOut

#-----------------------------------------------------------------------------------------

def convertAlignmentToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['A.a','A.f','A.b','A.s'], ['A.jo','A.g','A.fe']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertClassesToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['G'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertCraftsToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, [], ['CR']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)

    return strOutput

def convertCraftsToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, [], ['CR']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertDialogToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, [], ['D.q','D.a']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertDungeonsToJson(content: str) -> str:
    # Cas particulier de valeur m:new Object(), on commence par remplacer ces valeurs
    content = content.replace('m:new Object()', 'm:"new Object()"')
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['DU'], [])
    specialsValue = convertAllValidLineObjectWithMembrToJson(content, ['DU'], ['m'])
    if specialsValue != {}:
        jsonOut.update(specialsValue)
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertEffectsToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['E'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertEmotesToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['EM'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertFightChallengeToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['FC'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertGuildsToJson(content: str) -> str:
    # TODO ne fonctionne pas
    # TODO ajouter le support de l'extraction de 'GU.b'
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, [], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertHintsToJson(content: str) -> str:
    strOutput = ''
    jsonOut = convertAllValidLineObjectToJson(content, ['HIC'], []) 
    
    specialsValue = convertAllValidLineVariableWithArrayObjectToJson(content, ['HI'])
    if specialsValue != {}:
        jsonOut.update(specialsValue)
    
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertHousesToJson(content: str) -> str:
    # Ajout du support de H.d en modifiant en avant les attributs des éléments H.d qui sont particuliers:
    content = re.sub(r'([\{|\,])(c[0-9]*):', r'\1"\2":', content)

    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['H.h','H.d'], ['H.m']) 
    specialsValue = convertAllVariablesLinesToJson(content, ['H.ids'])
    if specialsValue != {}:
        jsonOut.update(specialsValue)

    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertInteractiveobjectsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['IO.d'], ['IO.g']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertItemsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['I.t','I.u'], ['I.st','I.ss']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput  

def convertItemstatsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, [], ['ISTA']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput 

def convertItemsetsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['IS'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput  

def convertJobsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['J'], [])  
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput   

def convertKbToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['KBC','KBA','KBT','KBD'], [])  
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertMapsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['MA.sa','MA.a','MA.m'], ['MA.sua']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertMonstersToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['MSR','MR','M'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertNamesToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, [], ['NF.n', 'NF.f']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertNpcToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['N.d'], ['N.a']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertPVPToJson(content: str) -> str:
    # TODO a reprendre
    # Fichier ignoré pour différentes raisons, les informations sont complexes à parser, le fichier est petit et ne contient pas beaucoup de chose
    # Elements: 'PP.hp', 'PP.maxdp', 'PP.grds'
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, [], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertQuestsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['Q.s','Q.o'], ['Q.q','Q.t'])  
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertRanksToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['R'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertRidesToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['RI','RIA'], [])  
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertScriptsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, [], ['SCR']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput  

def convertServersToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['SR','SRC','SRVT'], ['SRP', 'SRPW','SRVC']) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput  

def convertSkillsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['SK'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertSpeakingItemsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['SIM'], []) 
    specialsValue = convertAllVariablesArrayOfArrayLinesToJson(content, ['SIT'])
    if specialsValue != {}:
        jsonOut.update(specialsValue)

    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertSpellsToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['S'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertStatesToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['ST'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertTitlesToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['PT'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput

def convertTTGToJson(content: str) -> str:
    strOutput = ''      
    jsonOut = convertAllValidLineObjectToJson(content, ['TTG.c','TTG.e', 'TTG.f'], []) 
    strOutput = json.dumps(jsonOut, ensure_ascii=False, indent=2)
    return strOutput


def addFileInfosToJson(fileType: str, fileLanguage: str, fileVersion: str, jsonContent: str) -> str:
    if jsonContent == '{}':
        return '{}'


    output = {fileType:{'version': fileVersion, 'language':fileLanguage}}
    output[fileType].update(json.loads(jsonContent))
    return json.dumps(output, ensure_ascii=False, indent=2)


def scriptToJson(filename: str, script: str) -> str:
    # reçoit le type du swf et le contenu des scripts du swf et renvoi le contenu parser du swf
    fileInfos = filename.removesuffix('.swf').split('_')
    fileType = fileInfos[0]
    fileVersion = fileInfos[1]
    fileLanguage = fileInfos[2]
    
    match fileType:
        case 'alignment':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertAlignmentToJson(script))
        case 'classes':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertClassesToJson(script))
        case 'crafts':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertCraftsToJson(script))
        case 'dialog':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertDialogToJson(script))
        case 'dungeons':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertDungeonsToJson(script))
        case 'effects':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertEffectsToJson(script))
        case 'emotes':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertEmotesToJson(script))
        case 'fightChallenge':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertFightChallengeToJson(script))
        #case 'guilds':
            #return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertGuildsToJson(script))
        case 'hints':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertHintsToJson(script))
        case 'houses':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertHousesToJson(script))
        case 'interactiveobjects':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertInteractiveobjectsToJson(script))
        case 'items':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertItemsToJson(script))
        case 'itemsets':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertItemsetsToJson(script))
        case 'itemstats':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertItemstatsToJson(script))
        case 'jobs':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertJobsToJson(script))
        case 'kb':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertKbToJson(script))
        case 'maps':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertMapsToJson(script))
        case 'monsters':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertMonstersToJson(script))
        case 'names':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertNamesToJson(script))
        case 'npc':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertNpcToJson(script))
        #case 'pvp':
            #return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertPVPToJson(script))
        case 'quests':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertQuestsToJson(script))
        case 'ranks':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertRanksToJson(script))
        case 'rides':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertRidesToJson(script))
        case 'scripts':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertScriptsToJson(script))
        case 'servers':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertServersToJson(script))
        case 'skills':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertSkillsToJson(script))
        case 'speakingitems':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertSpeakingItemsToJson(script))
        case 'spells':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertSpellsToJson(script))
        case 'states':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertStatesToJson(script))
        case 'titles':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertTitlesToJson(script))
        case 'ttg':
            return addFileInfosToJson(fileType, fileVersion, fileLanguage, convertTTGToJson(script))
    return ""
