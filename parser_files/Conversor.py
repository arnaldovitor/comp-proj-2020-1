class Conversor:
    def __init__(self,symbols):
        self.symbols = symbols
        self.string = ""
        self.contador = 0
        self.condicao = ""
        self.linha = [0]
        
    def start(self):
        self.converterCod()

    def converterCod(self):
            i = 0;
            naoconta = ["END FUNC","END PROC","END WHILE","END IF","END ELSE","BREAK","CONTINUE"]
            identacao = 0
            while(i<len(self.symbols)):
                if(self.symbols[i][0] == "FUNC"):
                    i = self.codFUNC(i,identacao)
                elif(self.symbols[i][0] == "PROC"):
                    i = self.codPROC(i,identacao)
                elif(self.symbols[i][0] == "VAR"):
                    i = self.codVAR(i,identacao)
                elif(self.symbols[i][0] == "IF"):
                    i = self.codIF(i,identacao)
                elif(self.symbols[i][0] == "WHILE"):
                    i = self.codWHILE(i,identacao)
                elif(self.symbols[i][0] == "ELSE"):
                    i = self.codELSE(i,identacao)
                elif(self.symbols[i][0] in naoconta):
                    pass
                elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                    flag = self.codPRINTeRETURN(i,identacao)
                elif(self.symbols[i][0].isupper()):
                    self.codCALL(i,identacao)
                i+=1
            
            self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)
            print(self.string)

    #pronto
    def codFUNC(self, i,identacao):
        self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"{}:\n".format(self.symbols[i][1])
        identacao += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"BeginFunc\n"
        identacao += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        i+=1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "END FUNC"):
                break
            elif(self.symbols[i][0] == "IF"):
                i = self.codIF(i,identacao)
            elif(self.symbols[i][0] == "ELSE"):
                i = self.codELSE(i,identacao)
            elif(self.symbols[i][0] == "WHILE"):
                i = self.codWHILE(i,identacao)
            elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                i = self.codPRINTeRETURN(i,identacao)
            elif(self.symbols[i][0] == "VAR"):
                i = self.codVAR(i,identacao)
            elif(self.symbols[i][0].isupper()):
                i = self.codCALL(i,identacao)
            i+= 1
        identacao -=1
        self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"EndFunc\n"
        self.linha.append(self.linha[len(self.linha)-1]+1)
        return i

    #pronto
    def codPROC(self, i,identacao):
        self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"{}:\n".format(self.symbols[i][1])
        identacao += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"BeginFunc\n"
        identacao += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        i+=1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "END PROC"):
                break
            elif(self.symbols[i][0] == "IF"):
                i = self.codIF(i,identacao)
            elif(self.symbols[i][0] == "ELSE"):
                i = self.codELSE(i,identacao)
            elif(self.symbols[i][0] == "WHILE"):
                i = self.codWHILE(i,identacao)
            elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                i = self.codPRINTeRETURN(i,identacao)
            elif(self.symbols[i][0] == "VAR"):
                i = self.codVAR(i,identacao)
            elif(self.symbols[i][0].isupper()):
                i = self.codCALL(i,identacao)
            i+= 1
        identacao -=1
        self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"EndFunc\n"
        self.linha.append(self.linha[len(self.linha)-1]+1)
        return i

    #variavel pronto
    def codVAR(self, i,identacao):
        linha = self.symbols[i]
        if("(" in linha[3]):
            temp = linha[3].split("(")
            parametros = temp[1].replace(")","").split(",")
            for j in reversed(range(len(parametros))):
                self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"param {}\n".format(parametros[j])
                self.linha.append(self.linha[len(self.linha)-1]+1)
            self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"{} := call {},{}\n".format(linha[2],temp[0],len(parametros))
            self.linha.append(self.linha[len(self.linha)-1]+1)
        else:
            self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"{} := {}\n".format(linha[2],linha[3])
            self.linha.append(self.linha[len(self.linha)-1]+1)
        return i
    
    def codIF(self, i,identacao):
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"T{} :={}\n".format(self.contador,self.symbols[i][1])
        self.linha.append(self.linha[len(self.linha)-1]+1)
        self.condicao = "T{} :={}\n".format(self.contador,self.symbols[i][1])
        aux = self.condicao
        goto = "IF{}".format(self.contador)
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"if !T{} go to {}\n".format(self.contador,goto)
        self.contador += 1
        identacao += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        i+= 1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "END IF"):
                self.condicao = aux
                break
            elif(self.symbols[i][0] == "IF"):
                i = self.codIF(i,identacao)
            elif(self.symbols[i][0] == "ELSE"):
                i = self.codELSE(i,identacao)
            elif(self.symbols[i][0] == "WHILE"):
                i = self.codWHILE(i,identacao)
            elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                i = self.codPRINTeRETURN(i,identacao)
            elif(self.symbols[i][0] == "VAR"):
                i = self.codVAR(i,identacao)
            elif(self.symbols[i][0].isupper()):
                i = self.codCALL(i,identacao)
            i+=1
        identacao -= 1
        self.string = self.string.replace(goto,str(self.linha[len(self.linha)-1]+1))
        return i

    def codELSE(self,i,identacao):
        t = self.condicao.split(":")
        goto = "IF{}".format(self.contador)
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"if {}go to {}\n".format(t[0],goto)
        self.linha.append(self.linha[len(self.linha)-1]+1)
        i+=1
        identacao += 1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "END ELSE"):
                break
            elif(self.symbols[i][0] == "IF"):
                i = self.codIF(i,identacao)
            elif(self.symbols[i][0] == "ELSE"):
                i = self.codELSE(i,identacao)
            elif(self.symbols[i][0] == "WHILE"):
                i = self.codWHILE(i,identacao)
            elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                i = self.codPRINTeRETURN(i,identacao)
            elif(self.symbols[i][0] == "VAR"):
                i = self.codVAR(i,identacao)
            elif(self.symbols[i][0].isupper()):
                i = self.codCALL(i,identacao)
            i += 1
        identacao -=1
        self.string = self.string.replace(goto,str(self.linha[len(self.linha)-1]+1))
        return i
    
    def codWHILE(self, i,identacao):
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"L{}:\n".format(self.contador)
        self.linha.append(self.linha[len(self.linha)-1]+1)
        identacao += 1
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"T{} :={}\n".format(self.contador,self.symbols[i][1])
        self.linha.append(self.linha[len(self.linha)-1]+1)
        goto = "IF{}".format(self.contador)
        self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"if !T{} go to {}\n".format(self.contador,goto)
        aux = self.linha[len(self.linha)-1]
        self.contador += 1
        self.linha.append(self.linha[len(self.linha)-1]+1)
        identacao += 1
        i+=1
        while(i<len(self.symbols)):
            if(self.symbols[i][0] == "END WHILE"):
                self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"go to {}\n".format(aux+1)
                break
            elif(self.symbols[i][0] == "IF"):
                i = self.codIF(i,identacao)
            elif(self.symbols[i][0] == "ELSE"):
                i = self.codELSE(i,identacao)
            elif(self.symbols[i][0] == "WHILE"):
                i = self.codWHILE(i,identacao)
            elif(self.symbols[i][0] == "PRINT" or self.symbols[i][0] == "RETURN"):
                i = self.codPRINTeRETURN(i,identacao)
            elif(self.symbols[i][0] == "VAR"):
                i = self.codVAR(i,identacao)
            elif(self.symbols[i][0] == "BREAK" or self.symbols[i][0] == "CONTINUE"):
                self.string += "{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+self.symbols[i][0].lower()+"\n"
                self.linha.append(self.linha[len(self.linha)-1]+1)
            elif(self.symbols[i][0].isupper()):
                i = self.codCALL(i,identacao)
            i+= 1
        identacao -= 2
        self.string = self.string.replace(goto,str(self.linha[len(self.linha)-1]+2))
        self.linha.append(self.linha[len(self.linha)-1]+1)
        return i

    #PRINT e RETURN pronto
    def codPRINTeRETURN(self, i,identacao):
        linha = self.symbols[i]
        if(linha[0] == "PRINT"):
            for j in range(1,len(linha)-1):
                self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"print {}\n".format(linha[j])
                self.linha.append(self.linha[len(self.linha)-1]+1)
        elif(linha[0] == "RETURN"):
            self.string+="{}: ".format(self.linha[len(self.linha)-1]+1)+identacao*"\t"+"return {}\n".format(linha[2])
            self.linha.append(self.linha[len(self.linha)-1]+1)
        return i

    #call pronto
    def codCALL(self, i,identacao):
        linha = self.symbols[i]
        contador = 0
        for j in reversed(range(1,len(linha)-1)):
            self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"param {}\n".format(linha[j])
            self.linha.append(self.linha[len(self.linha)-1]+1)
            contador += 1
        self.string +="{}: ".format(self.linha[len(self.linha)-1]+1)+ identacao*"\t"+"call {},{}\n".format(linha[0],contador)
        self.linha.append(self.linha[len(self.linha)-1]+1)
        return i
