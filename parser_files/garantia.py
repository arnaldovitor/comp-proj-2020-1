from parser_files.Util import *
from lexer_files.Scanner import Scanner

class Semantic():
    def __init__(self, basedir, symbolsSemantic):
        self.symbols = symbolsSemantic
        
    def start(self):
        #valida para conferir que não há duas funções ou processos com mesmo nome
        self.validarTabela()

        #checagem de escopo
        linhas = []
        linhas = self.program.readlines()
        contadorReturn = 0
        contadorFunc = 0
        contadorPrint = 0
        for i in range(len(linhas)):
            lexer = Scanner(linhas[i])
            tableTokens = lexer.scan()
            #retorna um valor definido no escopo da função --- OK!
            if("RETURN " in linhas[i]):
                #RETURN variavel está funcionando
                if(tableTokens[1].type == "LETTER"):
                    #percorrer tabela de simbolos para verificar se a variavel esta no mesmo escopo que o return
                    returnCorreto = False
                    indiceFunc = self.getFuncIndex(contadorFunc)
                    contadorFunc += 1
                    indiceReturn = self.getReturnIndex(contadorReturn)
                    contadorReturn +=1
                    #percorre o escopo da função do return em questão
                    for j in range(indiceFunc,indiceReturn+1):
                        if(self.symbols[j][0] == "FUNC"):
                            aux = self.formatarLinha(linhas[i])
                            SentencasLinha = aux
                            if(tableTokens[1].lexeme in SentencasLinha):
                                returnCorreto = True    
                                break
                        elif(self.symbols[j][0] == "VAR"):
                            #verificar se a variavel ta no mesmo escopo que o return e está em um indice anterior ao return;
                            if(tableTokens[1].lexeme == self.symbols[j][2]):
                                returnCorreto = True
                                break
                    if(returnCorreto):
                        continue
                    else:
                        raise Exception('Semantic error (returning a variable that does not belongs to the function scope) in line{}'.format(i+1))
                            
                #RETURN valor;
                else:
                    continue;

            
            elif("PRINT(" in linhas[i] or "PRINT (" in linhas[i]):
                
                parametrosLinha = self.formatarLinha(linhas[i])
                escopoPrint = self.getPrintIndex(contadorPrint)
                contadorPrint += 1
                for j in range(1, len(tableTokens)):
                    #PRINT variavel
                    if(tableTokens[j].type == "LETTER"):
                        variavelMatch = False
                        #variavel nos parametros da funcao ou procedure
                        

                        #variavel foi declarada no escopo em que o print está
                        if(variavelMatch == False):
                            for k in range(len(self.symbols)):
                                if(self.symbols[k][0] == "VAR" and self.symbols[k][2] == tableTokens[j].lexeme and self.symbols[k][4] == escopoPrint):
                                    variavelMatch = True
                                    break
                            
                        #print dentro de um IF
                        if(variavelMatch == False):
                            pass
                        
                        if(variavelMatch):
                            continue
                        else:
                            raise Exception('Semantic error (printing a variable that does not belongs to the print scope) in line {}'.format(i+1))

                    #PRINT valor bruto;
                    else:
                        continue
            elif("INTEGER " in linhas[i]):
                pass
            elif("BOOLEAN " in linhas[i]):
                pass
            elif("IF " in linhas[i]):
                pass
            elif("WHILE " in linhas[i]):
                pass
            else:
                continue
            
        #validar a checagem de tipos passados corretamente
        for i in range(len(linhas)):
            if("FUNCTION" in linhas[i]):
                continue
            elif("PROCEDURE" in linhas[i]):
                continue
            elif("}" in linhas[i]):
                continue
            elif("CONTINUE" in linhas[i]):
                continue
            elif("BREAK" in linhas[i]):
                continue
            elif("ELSE" in linhas[i]):
                continue
            elif(linhas[i] == " " or linhas[i] == "\r" or linhas[i] == "\t"):
                continue
            else:
                #separa a linha atual em tokens
                lexer = Scanner(linhas[i])
                tableTokens = lexer.scan()
                j = 0
                while(j<len(tableTokens)):
                    #ajustar valores dos acrescimos de j
                    if(tableTokens[j].type == "IF"):
                        #pular o IF e o abre parenteses
                        j+= 2
                        #checkar expressão do if
                        j+= 1
                    elif(tableTokens[j].type == "WHILE"):
                        #pular o WHILE e o abre parenteses
                        j+= 2
                        #checkar condição do while
                        j += 1
                    elif(tableTokens[j].type == "LETTER" and tableTokens[j].lexeme.islower == True):
                        #pular a atribuição e ir direto para o começo da expressão
                        j+=2
                        tipo = tableTokens[j-1] 
                        #checkar expressão de variável e se expressão é do mesmo tipo que variável
                        j += 1
                    elif(tableTokens[j].type == "LETTER" and tableTokens[j].lexeme.isupper == True):
                        #pular o nome e ir direto para os parametros
                        j+=2
                        #chamada de procedure com passagem de parametro correta
                        j+= 1
                    elif(tableTokens[j].type == "PRINT"):
                        j+=2
                        #verificar se a variável está no mesmo escopo
                        j+= 1
                    elif(tableTokens[j].type == "RETURN"):
                        j+=1
                        #verificar se a variável está no mesmo escopo
                        j+= 1
                    else:
                        j += 1
        
    def validarTabela(self):
        for i in range(len(self.symbols)):
            for j in range(i+1,len(self.symbols)):
                if(self.symbols[i][0] == "FUNC"):
                    if(self.symbols[j][0] == "FUNC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a function declared earlier with the same name) in line{}'.format(i+1))
                    elif(self.symbols[j][0] == "PROC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a function declared earlier with the same name) in line{}'.format(i+1))
                elif(self.symbols[i][0] == "PROC"):
                    if(self.symbols[j][0] == "FUNC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a procedure declared earlier with the same name) in line{}'.format(i+1))
                    elif(self.symbols[j][0] == "PROC"):
                        if(self.symbols[i][1] == self.symbols[j][1]):
                            raise Exception('Semantic error (there are a procedure declared earlier with the same name) in line{}'.format(i+1))

    def getFuncIndex(self,indice):
        contador = 0
        for i in range(len(self.symbols)):
            if(self.symbols[i][0] == "FUNC"):
                if(contador == indice):
                    return i
                else:
                    contador += 1

    def getReturnIndex(self,indice):
        contador = 0
        for i in range(len(self.symbols)):
            if(self.symbols[i][0] == "RETURN"):
                if(contador == indice):
                    return i
                else:
                    contador += 1

    def formatarLinha(self, string):
        aux = string.replace("("," ").replace(")"," ").replace("{","").replace(","," ").replace(";","").replace("\t","").replace("\n","").replace("\r","").replace("  "," ")
        return aux.split(" ")        
                

    def getPrintIndex(self, indice):
        aux = self.scopes[indice].split(" ")
        return int(aux[len(aux)-2].replace(",",""))

    
    def paiEscopo(self, escopo):
        for i in range(len(self.symbols)):
            if(self.symbols[i][len(self.symbols[i])-2] == escopo):
                return int(self.symbols[i][len(self.symbols[i])-1])
    
