from swf.swfparser import *
from struct import unpack, pack

def actionsToActionScript(actions) -> str:
    actionscriptCode = ''
    constants = []
    stack = []
    branchOffset = [] # list pour les if et les jump, permet de connaitre le niveau d'indentation
    for action in actions:
        match action.name:
            case 'ActionConstantPool':
                constants = action.ConstantPool
            case 'ActionPush':

                match action.Type:
                    case 0:
                        # Type string literal?
                        stack.append('"' + action.String.replace('\"','\\"').replace('\n','\\n') + '"')
                    case 1:
                        # float
                        stack.append(action.Float)
                    case 2:
                        # valeur null
                        stack.append("null")
                    case 3:
                        # valeur undefind
                        stack.append("undefined")
                    case 4:
                        stack.append(action.RegisterNumber)
                    case 5:
                        stack.append("true" if action.Boolean == 1 else "false")
                    case 6:
                        # Lis une valeur double. 
                        stack.append(action.Double)
                    case 7:
                        #stack.append(action.Integer)
                        # extrait un int, comme le parser lit un uint32, on doit le convertir en i32
                        stack.append(unpack('l', pack('L', action.Integer & 0xffffffff))[0])
                    case 8:
                        stack.append('"' + constants[action.Constant8].replace('\"','\\"').replace('\n','\\n') + '"')
                    case 9:
                        stack.append('"' + constants[action.Constant16].replace('\"','\\"').replace('\n','\\n') + '"')

            case 'ActionSetVariable':                
                # HACK on retire les " mis autour des constantes
                variableValue = stack.pop()
                variableName = stack.pop().replace('"','')

                instruction = f"{variableName} = {variableValue};\n"
                actionscriptCode += instruction

            case 'ActionPop':
                if len(stack) > 0:
                    stack.pop()

            case 'ActionGetVariable':
                # pop la valeur et push la valeur avec un . en plus
                lastValue = stack.pop().replace('"','')
                stack.append(f"{lastValue}")

            case 'ActionGetMember':
                # on obtiens la valeur du membre d'un objet
                member = stack.pop()
                objectName = stack.pop().replace('"','')
                if type(member) == str:
                    stack.append(f"{objectName}.{member.replace('"','')}")
                elif type(member) == int:
                    stack.append(f"{objectName}[{str(member)}]")
                

            case 'ActionCallMethod':
                methodName = stack.pop().replace('"','')
                scriptObject = stack.pop().replace('"','')
                argsCount = stack.pop()
                args = []
                for _ in range(argsCount):
                    # on retire les args de la pile
                    args.append(stack.pop())
                # génère l'instruction
                instruction = f"{scriptObject}.{methodName}({", ".join(args)});\n"
                actionscriptCode += instruction
            case 'ActionNewObject':
                objectType = stack.pop().replace('"','')
                lenArgs = stack.pop()
                args = []
                for _ in range(lenArgs):
                    # on retire les args de la pile
                    args.append(stack.pop())

                stack.append(f"new {objectType}({", ".join(args)})")

            case 'ActionCallFunction':
                functionName = stack.pop().replace('"','')
                lenArgs = stack.pop()
                args = []
                for _ in range(lenArgs):
                    # on retire les args de la pile
                    args.append(str(stack.pop()))

                stack.append(f"{functionName}({", ".join(args)})")
            case 'ActionSetMember':
                newValue = stack.pop()
                objectName = stack.pop()
                popObject = stack.pop().replace('"','')
                if type(objectName) == str:
                    instruction = f"{popObject}.{objectName.replace('"','')} = {newValue};\n"
                else:
                    instruction = f"{popObject}[{objectName}] = {newValue};\n"
                actionscriptCode += instruction

            case 'ActionInitArray':
                arrayLen = stack.pop()
                arrayValues = "["
                for _ in range(arrayLen):
                    arrayValues += f"{stack.pop()},"
                arrayValues = (arrayValues[:-1] if len(arrayValues)>1 else arrayValues) + "]"
                stack.append(arrayValues)

            case 'ActionInitObject':
                objectInitValue = "{"
                nbObjectArgs = stack.pop()
                for _ in range(nbObjectArgs):
                    memberValue = stack.pop()
                    memberName = stack.pop()
                    objectInitValue += f"{memberName.replace('"','')}:{memberValue},"
                objectInitValue = objectInitValue[:-1] + "}"
                stack.append(objectInitValue)
            case 'ActionAdd2':
                arg1 = stack.pop()
                arg2 = stack.pop()
                result = arg2 + arg1
                result = result.replace('""""', '"') # cas ou une chaine vide est concatenée, on obtiens des chaines de " + "" + ", à transformer en un seul "
                result = result.replace('""','\"')
                stack.append(result)
            case 'ActionNot':
                value = stack.pop()
                newValue = ""
                if value[0] == '!':
                    newValue = value[1:]
                else:
                    newValue = "!" + value
                stack.append(newValue)
            case 'ActionPushDuplicate':
                value = stack[-1]
                stack.append(value)
            case 'ActionDefineLocal':
                # HACK on retire les " mis autour des constantes
                variableValue = stack.pop()
                variableName = stack.pop().replace('"','')

                instruction = f"var {variableName} = {variableValue};\n"
                actionscriptCode += instruction
            case 'ActionIncrement':
                value = stack.pop()
                value = (value +1) if type(value) == int else value + " + 1"
                stack.append(value)

            case 'ActionIf':
                instruction = ""
                if action.BranchOffset in branchOffset:
                    # si la branche existe déja, il s'agit de la même condition
                    actionscriptCode = actionscriptCode[:-3] # on retire les derniers caractères de la condition
                    instruction += f" || {stack.pop()}){{\n"
                else:
                    branchOffset.append(action.BranchOffset)
                    condition = stack.pop()
                    instruction = f"if({condition}){{\n"
                
                actionscriptCode += instruction
            case _ : 
                print(f"Tag inconnu: {action} - stack {stack}")

    return actionscriptCode



def extractScriptFromFile(filename: str) -> str:
    scripts = ""
    swf = parsefile(filename)

    for tag in swf.tags:
        if tag.name == 'DoAction':
            scripts += actionsToActionScript(tag.Actions)
    return scripts