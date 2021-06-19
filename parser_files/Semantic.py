from parser_files.Util import *
from lexer_files.Scanner import Scanner

class Semantic():
    def __init__(self, symbolsSemantic):
        self.symbols = symbolsSemantic
        
    def start(self):
        #valida para conferir que não há duas funções ou processos com mesmo nome
        self.validarTabela()
        #validação de escopo totalmente completa, validação de valores de variáveis completa, falta (IF, WHILE, CALLS)
        self.validarEscopo()

    def validarTabela(self):
        for i in range(len(self.symbols)):
            for j in range(i+1,len(self.symbols)):
                if(self.symbols[i][0] == "FUNC"):
                    if(self.symbols[j][0] == "FUNC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a function declared earlier with the same name) in line {}'.format(i+1))
                    elif(self.symbols[j][0] == "PROC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a function declared earlier with the same name) in line {}'.format(i+1))
                elif(self.symbols[i][0] == "PROC"):
                    if(self.symbols[j][0] == "FUNC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a procedure declared earlier with the same name) in line {}'.format(i+1))
                    elif(self.symbols[j][0] == "PROC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a procedure declared earlier with the same name) in line {}'.format(i+1))

    def validarEscopo(self):
        contadorIF = 0
        contadorELSE = 0
        contadorWHILE = 0
        i= 0
        variaveis = []
        naoconta = ["END FUNC","END PROC","END WHILE","END IF","END ELSE","BREAK","CONTINUE"]
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "FUNC"):
                i = self.escopoFUNC(i)
            elif(self.symbols[i][0] == "PROC"):
                i = self.escopoPROC(i)
            elif(self.symbols[i][0] == "VAR"):
                existe = False
                for j in range(len(variaveis)):
                    if(variaveis[j][1] == self.symbols[i][2]):
                        existe = True
                        break
                if(not existe):
                    variaveis.append(self.symbols[i][1:3])
                self.varChecagem(self.symbols[i],variaveis)
            elif(self.symbols[i][0] == "IF"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],variaveis)
                i = self.escopoIF(i,variaveis)
            elif(self.symbols[i][0] == "WHILE"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],variaveis)
                i = self.escopoWHILE(i,variaveis)
                #
            elif(self.symbols[i][0] == "ELSE"):
                i = self.escopoIF(i,variaveis)
            elif(self.symbols[i][0] in naoconta):
                pass
            elif(self.symbols[i][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[i],variaveis,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the scope) in line {}'.format(self.symbols[i][len(self.symbols[i])-1]))
            elif(self.symbols[i][0].isupper()):
                self.escopoCALL(self.symbols[i],variaveis)
                #
            i+=1

    def escopoFUNC(self,i):
        variaveisFunc = []
        #verifica as variáveis nos parametros da função
        for j in range(7,len(self.symbols[i]),6):
            aux = []
            aux.append(self.symbols[i][j-1])
            aux.append(self.symbols[i][j])
            variaveisFunc.append(aux)
        j = i+1
        while(j<len(self.symbols)):
            if(self.symbols[j][0] == "END FUNC"):
                return j;
                    
            elif(self.symbols[j][0] == "VAR"):
                if(len(self.symbols[j][4])>0):
                    for k in range(len(self.symbols[j][4])):
                        presente = False
                        for m in range(len(variaveisFunc)):
                            if(self.symbols[j][4][k] == variaveisFunc[m][1]):
                                presente = True
                                break
                        if(not presente):
                            raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
                aux = []
                aux.append(self.symbols[j][1])
                aux.append(self.symbols[j][2])
                variaveisFunc.append(aux)
                self.varChecagem(self.symbols[i],variaveisFunc)
            elif(self.symbols[j][0] == "IF"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoIF(j,variaveisFunc)
            elif(self.symbols[j][0] == "ELSE"):
                j = self.escopoELSE(j, variaveisFunc)
            elif(self.symbols[j][0] == "WHILE"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoWHILE(j,variaveisFunc)
            elif(self.symbols[j][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            elif(self.symbols[j][0] == "RETURN"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,1)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            elif(self.symbols[j][0].isupper()):
                escopoCALL(self.symbols[j],variaveisFunc)
            j+=1

    def escopoPROC(self,i):
        variaveisFunc = []
        #verifica as variáveis nos parametros da função
        for j in range(7,len(self.symbols[i]),6):
            aux = []
            aux.append(self.symbols[i][j-1])
            aux.append(self.symbols[i][j])
            variaveisFunc.append(aux)
        j = i+1
        while(j<len(self.symbols)):
            if(self.symbols[j][0] == "END PROC"):
                return j;
                    
            elif(self.symbols[j][0] == "VAR"):
                if(len(self.symbols[j][4])>0):
                    for k in range(len(self.symbols[j][4])):
                        presente = False
                        for m in range(len(variaveisFunc)):
                            if(self.symbols[j][4][k] == variaveisFunc[m][1]):
                                presente = True
                                break
                        if(not presente):
                            raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
                aux = []
                aux.append(self.symbols[j][1])
                aux.append(self.symbols[j][2])
                variaveisFunc.append(aux)
                self.varChecagem(self.symbols[i],variaveisFunc)
            elif(self.symbols[j][0] == "IF"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoIF(j,variaveisFunc)
            elif(self.symbols[j][0] == "ELSE"):
                j = self.escopoELSE(j, variaveisFunc)
            elif(self.symbols[j][0] == "WHILE"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoWHILE(j,variaveisFunc)
            elif(self.symbols[j][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            elif(self.symbols[j][0].isupper()):
                escopoCALL(self.symbols[j],variaveisFunc)
            j+=1

    def escopoCALL(self,linha,var):
        flag = False
        for i in range(len(self.symbols)):
            if(self.symbols[i][0] == "FUNC" or self.symbols[i][0] == "PROC"):
                if(linha[0] == self.symbols[i][1]):
                    variaveisChamada = []
                    for j in range(1,len(linha)-1):
                        variaveisChamada.append(linha[j])
                    varDeclaracao = []
                    varTipagem = []
                    for j in range(7,len(self.symbols[i])-1,6):
                        varDeclaracao.append(self.symbols[i][j])
                        varTipagem.append(self.symbols[i][j-1])
                    if(len(variaveisChamada) != len(varDeclaracao)):
                        raise Exception('Semantic error (declaration has {} arguments but {} arguments was given) in line {}'.format(len(varDeclaracao),len(variaveisChamada),linha[len(linha)-1]))
                    #variáveis da chamada a partir do indice 1 até o indice tamanho - 2
                    #variaveis na self.symbols começam a partir do indice i=7 e o tipo é definido em i-1, pulando de 6 em 6 a cada nova variável
                    else:
                        tipagemChamada = []
                        for j in range(len(variaveisChamada)):
                            if(variaveisChamada[j].isnumeric()):
                                tipagemChamada.append("INTEGER")
                            elif(variaveisChamada[j] in ["True","False"]):
                                tipagemChamada.append("BOOLEAN")
                            else:
                                for k in range(len(var)):
                                    if(var[k][1] == variaveisChamada[j]):
                                        tipagemChamada.append(var[k][0])
                                        break
                        if(tipagemChamada == varTipagem):
                            flag = True
                            break
                        else:
                            raise Exception('Semantic error (parameters declaration type differs from call parameters type) in line {}'.format(linha[len(linha)-1])) 
        if(not flag):
            raise Exception('Semantic error (function or procedure not declared) in line {}'.format(linha[len(linha)-1]))
        flag = self.escopoPRINTeRETURN(linha,var,0)
        if(not flag):
             raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(linha[len(linha)-1])) 

    def escopoIF(self,indice,aux):
        var = aux.copy()
        i = indice+1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "IF"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoIF(i,var)
            elif(self.symbols[i][0] == "END IF"):
                return i
            elif(self.symbols[i][0] == "ELSE"):
                i = self.escopoELSE(i, var)
            elif(self.symbols[i][0] == "WHILE"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoWHILE(i, var)
            elif(self.symbols[i][0] == "VAR"):
                if(len(self.symbols[i][4])>0):
                    for k in range(len(self.symbols[i][4])):
                        presente = False
                        for m in range(len(var)):
                            if(self.symbols[j][4][k] == var[m][1]):
                                presente = True
                                break
                        if(not presente):
                            raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
                aux = []
                aux.append(self.symbols[i][1])
                aux.append(self.symbols[i][2])
                var.append(aux)
                self.varChecagem(self.symbols[i],var)
            elif(self.symbols[i][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[i],var,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[i][len(self.symbols[i])-1]))
            elif(self.symbols[i][0].isupper()):
                self.escopoCALL(self.symbols[i],var)
            i+=1

    def escopoELSE(self,indice,aux):
        var = aux.copy()
        i = indice+1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "IF"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoIF(i,var)
            elif(self.symbols[i][0] == "END ELSE"):
                return i
            elif(self.symbols[i][0] == "ELSE"):
                i = self.escopoELSE(i, var)
            elif(self.symbols[i][0] == "WHILE"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoWHILE(i, var)
            elif(self.symbols[i][0] == "VAR"):
                if(len(self.symbols[i][4])>0):
                    for k in range(len(self.symbols[i][4])):
                        presente = False
                        for m in range(len(var)):
                            if(self.symbols[j][4][k] == var[m][1]):
                                presente = True
                                break
                        if(not presente):
                            raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
                aux = []
                aux.append(self.symbols[i][1])
                aux.append(self.symbols[i][2])
                var.append(aux)
                self.varChecagem(self.symbols[i],var)
            elif(self.symbols[i][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[i],var,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[i][len(self.symbols[i])-1]))
            elif(self.symbols[i][0].isupper()):
                self.escopoCALL(self.symbols[i],var)
            i+=1
    def escopoWHILE(self,indice,aux):
        var = aux.copy()
        i = indice+1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "IF"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoIF(i,var)
            elif(self.symbols[i][0] == "END WHILE"):
                return i
            elif(self.symbols[i][0] == "ELSE"):
                i = self.escopoELSE(i, var)
            elif(self.symbols[i][0] == "WHILE"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],var)
                i = self.escopoWHILE(i, var)
            elif(self.symbols[i][0] == "VAR"):
                if(len(self.symbols[i][4])>0):
                    for k in range(len(self.symbols[i][4])):
                        presente = False
                        for m in range(len(var)):
                            if(self.symbols[j][4][k] == var[m][1]):
                                presente = True
                                break
                        if(not presente):
                            raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
                aux = []
                aux.append(self.symbols[i][1])
                aux.append(self.symbols[i][2])
                var.append(aux)
                self.varChecagem(self.symbols[i],var)
            elif(self.symbols[i][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[i],var,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[i][len(self.symbols[i])-1]))
            elif(self.symbols[i][0] == "BREAK" or self.symbols[i][0] == "CONTINUE"):
                pass
            elif(self.symbols[i][0].isupper()):
                self.escopoCALL(self.symbols[i],var)
            i+=1

    def escopoPRINTeRETURN(self,linha,var,tipo):
        tipagem = ["INTEGER","BOOLEAN"]
        if(tipo == 0):
            for i in range(1,len(linha)-1):
                if(linha[i] not in tipagem):
                    if(linha[i].isnumeric()):
                        continue
                    if(linha[i] == 'False' or linha[i] == 'True'):
                        continue
                    else:
                        flag = False
                        for j in range(len(var)):
                            if(isinstance(var[j],list)):
                                if(linha[i] == var[j][1]):
                                    flag = True
                                    break
                            else:
                                if(linha[i] == var[j]):
                                    flag = True
                                    break
                        if(not flag):
                            return False
        else:
            for i in range(2,len(linha)-3,2):
                if(linha[i] not in tipagem):
                    if(linha[i].isnumeric()):
                        return True
                    if(linha[i] == 'False' or linha[i] == 'True'):
                        return True
                    else:
                        for j in range(len(var)):
                            if(isinstance(var[j],list)):
                                if(linha[i] == var[j][1]):
                                    return True
                            else:
                                if(linha[i] == var[j]):
                                    return True
                        return False
        return True

    def varChecagem(self,var,vetorVariaveis):
        varAux = var.copy()
        vetorAux = vetorVariaveis.copy()
        tipo = varAux[1]
        varTipagems = []
        for i in range(len(vetorAux)):
            if(vetorAux[i][1] == var[2]):
                if(vetorAux[i][0] != var[1]):
                    raise Exception('Semantic error (variable already declared with another type) in line {}'.format(var[len(var)-1]))
                
        if(len(varAux[4])>0):
            for i in range(len(varAux[4])):
                for j in range(len(vetorAux)):
                    if(isinstance(vetorAux[j],list)):
                        if(varAux[4][i] == vetorAux[j][1]):
                            varTipagems.append(vetorAux[j][0])
                            break
                        
        aritmetic = ["+","-","*","/"]
        boolean = [">","<","==","!=",">=","<="]
        tipagem = ""
        for i in range(len(aritmetic)):
            if(isinstance(varAux[3],int) == False and varAux[3] not in ["True","False"]):
                if(aritmetic[i] in varAux[3]):
                    tipagem = "INTEGER"
                    break
        for i in range(len(boolean)):
            if(isinstance(varAux[3],int) == False and varAux[3] not in ["True","False"]):
                if(boolean[i] in varAux[3]):
                    tipagem = "BOOLEAN"
                    break
        if(tipagem != ""):
            if(tipagem != tipo):
                raise Exception('Semantinc error (variable type differs from operation type) in line {}'.format(var[len(var)-1]))
            else:
                 if(len(varTipagems) == 0):
                    pass
                 elif(len(varTipagems) == 1):
                    if(("True" in varAux[3]) or ("False" in varAux[3])):
                        if("==" in varAux[3] or "!=" in varAux[3]):
                            if(varTipagems[0] != "BOOLEAN"):
                                raise Exception('Semantinc error (operation between different types) in line {}'.format(var[len(var)-1]))
                        else:
                            raise Exception('Semantinc error (operation between different types) in line {}'.format(var[len(var)-1]))
                    if(varAux[3][0].isnumeric()):
                        if(varTipagems[0] != "INTEGER"):
                            raise Exception('Semantinc error (operation between different types) in line {}'.format(var[len(var)-1]))
                    elif(varAux[3][2].isnumeric()):
                        if(varTipagems[0] != "INTEGER"):
                            raise Exception('Semantinc error (operation between different types) in line {}'.format(var[len(var)-1]))
                 else:
                    if(varTipagems[0] != varTipagems[1]):
                        raise Exception('Semantinc error (operation between different types) in line {}'.format(var[len(var)-1]))
                    elif(tipagem != tipo):
                        raise Exception('Semantinc error (variable type differs from operation type) in line {}'.format(var[len(var)-1]))
                
        elif(len(varAux[4])>0):
            for i in range(len(vetorAux)):
                if(vetorAux[i][1] == varAux[4][0]):
                    if(vetorAux[i][0] != varAux[1]):
                        raise Exception('Semantinc error (variable type differs from attribution type) in line {}'.format(var[len(var)-1]))
        else:
            if(varAux[3].isnumeric()):
                if(tipo != "INTEGER"):
                    raise Exception('Semantinc error (variable of type BOOLEAN receving an INTEGER value) in line {}'.format(var[len(var)-1]))
            elif(varAux[3] in ["True","False"]):
                if(tipo != "BOOLEAN"):
                    raise Exception('Semantinc error (variable of type INTEGER receving a BOOLEAN value) in line {}'.format(var[len(var)-1]))
            else:
                nome = varAux[3].split("(")
                for i in range(len(self.symbols)):
                    if(self.symbols[i][0] == "FUNC"):
                        if(self.symbols[i][1] == nome[0]):
                            for j in range(i+1,len(self.symbols)):
                                if(self.symbols[j][0] == "RETURN"):
                                    if((tipo == "INTEGER" and self.symbols[j][1] == "BOOLEAN") or tipo == "BOOLEAN" and self.symbols[j][1] != "BOOLEAN"):
                                        raise Exception('Semantic erro (variable and function return of different types) in line {}'.format(varAux[len(varAux)-1]))

    def checkExpression(self,expressao,linha,variaveis):
        expressao = expressao.replace(" ","")
        aritmetic = ["+","-","*","/"]
        boolean = [">","<","==","!=",">=","<="]
        tipo = ["",""]
        if(expressao.isnumeric()):
            raise Exception('Semantic error (condition can not be an integer value) in line {}'.format(linha))
        elif(expressao in ["True","False"]):
            pass
        else:
            for i in range(len(aritmetic)):
                if(aritmetic[i] in expressao):
                    raise Exception('Semantic error (condition can not be an aritmetic expression) in line {}'.format(linha))
            for i in range(len(boolean)):
                if(boolean[i] in expressao):
                    aux = expressao.split(boolean[i])
                    for j in range(len(aux)):
                        if(aux[j].isnumeric() == False and aux[j] not in ["True","False"]):
                            for k in range(len(variaveis)):
                                if(variaveis[k][1] == aux[j]):
                                    tipo[j] = variaveis[k][0]
                                    break
                            if(tipo[j] == ""):
                                raise Exception('Semantic error (condition has a variable not declared) in line {}'.format(linha))
                        elif(aux[j].isnumeric()):
                            tipo[j] = "INTEGER"
                            continue
                        elif(aux[j] in ["True","False"]):
                            tipo[j] = "BOOLEAN"
                            continue
                    if(tipo[0] != tipo[1]):
                        raise Exception('Semantic error (condition can not compare different types of argument) in line {}'.format(linha))
                
    

        
