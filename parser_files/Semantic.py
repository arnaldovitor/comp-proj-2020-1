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

    #verifica se não há duas funções ou dois procedures com o mesmo nome
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

    #valida escopo do programa (escopo a nível global)
    def validarEscopo(self):
        contadorIF = 0
        contadorELSE = 0
        contadorWHILE = 0
        i= 0
        variaveis = []
        naoconta = ["END FUNC","END PROC","END WHILE","END IF","END ELSE","BREAK","CONTINUE"]
        while(i<len(self.symbols)):
            #valida escopo de função
            if(self.symbols[i][0] == "FUNC"):
                i = self.escopoFUNC(i)
            #valida escopo de procedures
            elif(self.symbols[i][0] == "PROC"):
                i = self.escopoPROC(i)
            #valida escopo de variáveis
            elif(self.symbols[i][0] == "VAR"):
                existe = False
                #confere se a variável realmente existe, checando a tabela de símbolos
                for j in range(len(variaveis)):
                    if(variaveis[j][1] == self.symbols[i][2]):
                        existe = True
                        break
                if(not existe):
                    variaveis.append(self.symbols[i][1:3])
                #checa a tipagem da variável e da associação do valor dela
                self.varChecagem(self.symbols[i],variaveis)
            #valida IFs
            elif(self.symbols[i][0] == "IF"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],variaveis)
                i = self.escopoIF(i,variaveis)
            #valida WHILEs
            elif(self.symbols[i][0] == "WHILE"):
                self.checkExpression(self.symbols[i][1],self.symbols[i][2],variaveis)
                i = self.escopoWHILE(i,variaveis)
            #valida ELSEs
            elif(self.symbols[i][0] == "ELSE"):
                i = self.escopoIF(i,variaveis)
            #pula linhas que identificam o termino de blocos, brek e continue
            elif(self.symbols[i][0] in naoconta):
                pass
            #valida PRINTs
            elif(self.symbols[i][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[i],variaveis,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the scope) in line {}'.format(self.symbols[i][len(self.symbols[i])-1]))
            #valida chamadas de função e procedures
            elif(self.symbols[i][0].isupper()):
                self.escopoCALL(self.symbols[i],variaveis)
            i+=1

    #valida escopo de Função
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

            #valida declaração de variáveis dentro de funções e checa a tipagem da atribuição
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
            #valida IFs dentro de funções
            elif(self.symbols[j][0] == "IF"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoIF(j,variaveisFunc)
            #valida ELSEs dentro de funções
            elif(self.symbols[j][0] == "ELSE"):
                j = self.escopoELSE(j, variaveisFunc)
            #valida WHILE dentro de funções
            elif(self.symbols[j][0] == "WHILE"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoWHILE(j,variaveisFunc)
            #valida PRINTs dentro de funções
            elif(self.symbols[j][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            #valida o retorno da função
            elif(self.symbols[j][0] == "RETURN"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,1)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            #valida chamada de funções e procedures dentro da função
            elif(self.symbols[j][0].isupper()):
                escopoCALL(self.symbols[j],variaveisFunc)
            j+=1

    #valida a semantica de procedures
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
            #valida declaração de variáveis dentro de procedures e a tipagem de sua atribuição
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
            #valida IFs dentro de procedures
            elif(self.symbols[j][0] == "IF"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoIF(j,variaveisFunc)
            #valida ELSEs dentro de procedures
            elif(self.symbols[j][0] == "ELSE"):
                j = self.escopoELSE(j, variaveisFunc)
            #valida WHILE dentro de procedures
            elif(self.symbols[j][0] == "WHILE"):
                self.checkExpression(self.symbols[j][1],self.symbols[j][2],variaveisFunc)
                j = self.escopoWHILE(j,variaveisFunc)
            #valida PRINT dentro de procedures
            elif(self.symbols[j][0] == "PRINT"):
                flag = self.escopoPRINTeRETURN(self.symbols[j],variaveisFunc,0)
                if(not flag):
                    raise Exception('Semantic error (variable not declared in the function scope) in line {}'.format(self.symbols[j][len(self.symbols[j])-1]))
            #valida chamada de função ou procedure dentro de procedures
            elif(self.symbols[j][0].isupper()):
                escopoCALL(self.symbols[j],variaveisFunc)
            j+=1

    #valida chamada de funções
    def escopoCALL(self,linha,var):
        flag = False
        #valida para ver se as variáveis passadas estão de acordo com a chamada, em tipagem e quantidade
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

    #valida IF
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

    #valida ELSE
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

    #valida WHILE
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

    #valida PRINT e RETURN
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

    #confere a checagem da variável com a atribuição que está sendo feita
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

    #checa se a expressão condiz com os parâmetros e tipo da expressão
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
                
    

        
