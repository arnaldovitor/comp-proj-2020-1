from parser_files.Util import *

class Parser():
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens
        self.flag = 0
        self.expression = ""
        self.symbols = []
        self.scopes = [0]
        self.currentScope = 0
        self.scopoPai = 0
        self.listScopos = []
        self.symbolsSemantic = []
        
    #retorna o token atual
    def getCurrentToken(self):
        return self.tokens[self.current]

    #retorna o lookahead token
    def getLookAheadToken(self):
        return self.tokens[self.current + 1]

    #main
    def start(self):
        self.statementList()
        return

    #função que verifica se o programa terminou, se não executa a recursão para chamar-la novamente
    def statementList(self):
        if self.getCurrentToken().type == "END":
            return
        else:
            self.statement()
            self.statementList()
            return

    #Define o tipo de chamada que será feita
    def statement(self):
        systemCalls = ["IF", "WHILE", "PRINT", "RETURN"]
        #Declaração de variáveis
        if self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN":
            self.varStatement()
            return
        #Declaração de função
        elif self.getCurrentToken().type == "FUNCTION":
            self.funcStatement()
            return
        #Declaração de procedure
        elif self.getCurrentToken().type == "PROCEDURE":
            self.procStatement()
            return
        #chamada de função ou de processo
        elif self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True:
            self.callStatement()
            return
        #System calls
        elif self.getCurrentToken().type in systemCalls:
            self.systemCallStatement()
            return
        else:
            raise Exception('Syntatic error (variable initialized without type) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para cadeia de tokens que começam com INTEGER ou BOOLEAN
    def varStatement(self):
        booleanOperation = [">","<",">=","<=","==","!=","True","False"]
        aux = []
        aux.append('VAR')
        aux.append(self.getCurrentToken().type)
        self.current += 1
        #após tipagem deve haver nome da variável
        if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower():
            aux.append(self.getCurrentToken().lexeme)
            self.current += 1
            #símbolo de atribuição é necessário após nome da variável
            if self.getCurrentToken().type == "ATTR":
                self.current += 1
                #Guarda valor da linha e chega o valor da atribuição da variável
                line = self.getCurrentToken().line
                atributos = self.checkExpression(aux[1])
                #pega valor da expressão
                auxExpression = self.expression      
                aux.append(auxExpression)
                aux.append(atributos)
                self.expression = ""
                #verifica se após a atribuição existe um ;
                if self.getCurrentToken().type == "SEMICOLON":
                    aux.append(self.currentScope)
                    aux.append(self.scopoPai)
                    linha = self.getCurrentToken().line
                    self.current += 1
                    self.symbols.append(aux)
                    aux.append(linha)
                    self.symbolsSemantic.append(aux)
                    return
                #há alguma coisa escrita após a declaração da variável e atribuição de valor
                elif self.getCurrentToken().line == line and self.getCurrentToken().type != "END":
                    raise Exception(
                        'Syntatic error (expressions must be at most between two operands) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting ; after variable declaration) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting = in variable declaration) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (expecting a variable name) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para expressões lógicas ou aritméticas
    def checkExpression(self,tipo):
        parameters = ["INTEGER", "BOOLEAN","NUM"]
        #Validação de expressões númericas
        semanticValues = []
        if self.getCurrentToken().type == "NUM":
            # passa para declaração simples de integer
            if hasLogicSymbol(self.getLookAheadToken()) == False:
                #Declaração de um valor numérico
                if hasArithmeticSymbol(self.getLookAheadToken()) == False:
                    self.expression+=self.getCurrentToken().lexeme
                    self.current += 1
                    return semanticValues
                else:
                    # Operação aritmética do tipo num + num ou num+variável
                    self.expression += self.getCurrentToken().lexeme
                    self.current += 1
                    if self.getLookAheadToken().type == "NUM" or self.getLookAheadToken().type == "LETTER":
                        self.expression+=self.getCurrentToken().lexeme
                        self.expression+=self.getLookAheadToken().lexeme
                        if(self.getLookAheadToken().type == "LETTER"):
                            semanticValues.append(self.getLookAheadToken().lexeme)
                        self.current += 2
                        return semanticValues
                    else:
                        # nega casos num + /
                        raise Exception('Syntatic error (arithmetic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                # casos que tem expressões lógicas
                self.expression+=self.getCurrentToken().lexeme
                self.current += 1
                # passa para casos como num > num
                if self.getLookAheadToken().type == "NUM":
                    self.expression+=self.getCurrentToken().lexeme
                    self.expression+=self.getLookAheadToken().lexeme
                    self.current += 2
                    return semanticValues
                # passa para casos como num > var
                elif self.getLookAheadToken().type == "LETTER":
                    if self.getLookAheadToken().lexeme.islower():
                        self.expression += self.getCurrentToken().lexeme
                        self.expression += self.getLookAheadToken().lexeme
                        semanticValues.append(self.getLookAheadToken().lexeme)
                        self.current += 2
                        return semanticValues
                    # passa para casos como num > function()
                    elif self.getLookAheadToken().lexeme.isupper():
                        self.expression += self.getCurrentToken().lexeme
                        self.expression += self.getLookAheadToken().lexeme
                        self.current += 2
                        #Parâmetros da chamada da função
                        if self.getCurrentToken().type == "POPEN":
                            self.expression += self.getCurrentToken().lexeme
                            self.current += 1
                            #Leitura de todos os parametros das função
                            while self.getCurrentToken().type != "PCLOSE":
                                if self.getCurrentToken().type == "NUM" or self.getCurrentToken().type == "BOOLEAN" or self.getCurrentToken().lexeme.islower():
                                    self.expression += self.getCurrentToken().lexeme
                                    self.current += 1
                                    #Existência de vírgulas separando os paramêtros
                                    if self.getCurrentToken().type == "COMMA":
                                        self.expression += self.getCurrentToken().lexeme
                                        self.current += 1
                                        #Fecha parenteses com uma virgula antes (Ex,)
                                        if self.getCurrentToken().type == "PCLOSE":
                                            raise Exception('Syntatic error (expecting more arguments) in line {}'.format(self.getCurrentToken().line))
                                    #Fecha parenteses
                                    elif self.getCurrentToken().type == "PCLOSE":
                                        self.expression += self.getCurrentToken().lexeme
                                        self.current += 1
                                        break
                                    else:
                                        raise Exception('Syntatic error (unexpect comma) in line {}'.format(self.getCurrentToken().line))
                                else:
                                    raise Exception('Syntatic error (invalid argument) in line {}'.format(self.getCurrentToken().line))
                        else:
                            raise Exception('Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception('Syntatic error (expecting operation with function or variable) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting a logical expression) in line {}'.format(self.getCurrentToken().line))
                
        elif self.getCurrentToken().type == "LETTER":
            # declaração de var recebendo function
            if self.getCurrentToken().lexeme.isupper():
                self.expression += self.getCurrentToken().lexeme
                self.current += 1
                #Declaração de parenteses para parametros da função
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.expression += self.getCurrentToken().lexeme
                    self.current += 1
                    commaflag = False
                    #Leitura os parametros
                    while self.getCurrentToken().type != "PCLOSE":
                        #Parentese para passagem de parametros não foi fechado
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception('Syntatic error (expecting paranteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        #Declaração dos parametros
                        elif self.getCurrentToken().type in parameters:
                            #Identifica se há uma chamada de função ou procedure como parametro, que não é permitido
                            if self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getLookAheadToken().line))
                            #Identifica se há um identificador de tipagem para uma variável
                            elif self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == True:
                                self.expression += self.getCurrentToken().lexeme
                                self.expression += self.getLookAheadToken().lexeme
                                self.current += 2
                                commaflag = True
                            #Parametro válido
                            else:
                                #Leu um parametro sem que houvesse separação por virgulas
                                if(commaflag == True):
                                    raise Exception('Syntatic error (a comma was expected to be between two parameters) in line {}'.format(self.getCurrentToken().line))
                                self.expression += self.getCurrentToken().lexeme
                                self.current += 1
                                commaflag = True
                        #Lendo vírgula que separa os parametros
                        elif self.getCurrentToken().type == "COMMA" and commaflag == True:
                            if self.getLookAheadToken().type == "PCLOSE":
                               raise Exception('Syntatic error (expecting an argument after comma) in line{}'.format(self.getCurrentToken().line))
                            self.expression += self.getCurrentToken().lexeme
                            self.expression += self.getLookAheadToken().lexeme
                            self.current += 2
                            commaflag = False
                        else:
                            raise Exception('Syntatic error (invalid function ou procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.expression+=self.getCurrentToken().lexeme
                    self.current+=1
                    return semanticValues
                else:
                    raise Exception('Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
            #Declaração de variável recebendo variável
            elif self.getCurrentToken().lexeme.islower():
                semanticValues.append(self.getCurrentToken().lexeme)
                #confere a atribuição de operação
                if hasLogicSymbol(self.getLookAheadToken()) or hasArithmeticSymbol(self.getLookAheadToken()):
                    self.expression+=self.getCurrentToken().lexeme
                    self.expression+=self.getLookAheadToken().lexeme
                    self.current += 2
                    if self.getCurrentToken().type == "NUM" or self.getCurrentToken().type == "BOOLEAN" or self.getCurrentToken().lexeme.islower():
                        if(self.getCurrentToken().lexeme.islower()):
                            semanticValues.append(self.getCurrentToken().lexeme)
                        self.expression+=self.getCurrentToken().lexeme
                        self.current += 1
                        return semanticValues
                    else:
                        raise Exception('Syntatic error (incomplete logic/arithmetic expression) in line {}'.format(self.getCurrentToken().line))
                else:
                    if self.getLookAheadToken().type == "SEMICOLON":
                        self.expression+=self.getCurrentToken().lexeme
                        self.current+=1
                        return semanticValues
                    else:
                        raise Exception('Syntatic error (incomplete logic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting function name is upper or variable name is lower in line {}'.format(self.getCurrentToken().line))
        #Validação através de condição = valor booleano
        elif self.getCurrentToken().type == "BOOLEAN":
            self.expression+=self.getCurrentToken().lexeme
            self.current += 1
            return semanticValues
        else:
            raise Exception('Syntatic error expression in line {}'.format(self.getCurrentToken().line))

    # análise sintática de escopo
    def scopoStatement(self, tipo):
        total = ["SEMICOLON", "LETTER", "IF", "WHILE", "PRINT", "INTEGER", "BOOLEAN", "RETURN", "BREAK", "CONTINUE"]
        parameters = ["INTEGER", "BOOLEAN", "LETTER"]
        systemCalls = ["IF", "WHILE", "PRINT", "RETURN"]
        
        if(self.getCurrentToken().type not in total):
            raise Exception('Syntatic error (unexpect agurment in scopo) in line {}'.format(self.getCurrentToken().line))
        #verifica os elementos do escopo de uma função ou procedure
        while self.getCurrentToken().type in total:
            #Declaração de System call
            if self.getCurrentToken().type in systemCalls:
                if(tipo == 0 or tipo == 2):
                    self.systemCallStatement()
                elif(tipo == 1):
                    if(self.getCurrentToken().type == "RETURN"):
                        raise Exception('Syntatic error (procedures do not have a RETURN) in line{}'.format(self.getCurrentToken().line))
                    else:
                        self.systemCallStatement()
            #Declaração de variável
            elif self.getCurrentToken().type in parameters:
                #Chamada de função
                if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True:
                    self.callStatement()
                #Declaração ou chamada de variável
                else:
                    self.varStatement()
            #Validação de ; para fechar linha
            elif self.getCurrentToken().type == "SEMICOLON":
                self.current += 1
            elif (self.getCurrentToken().type == "BREAK" or self.getCurrentToken().type == "CONTINUE") and tipo == 2:
                if self.getLookAheadToken().type == "SEMICOLON":
                    self.symbolsSemantic.append([self.getCurrentToken().lexeme, self.getCurrentToken().line])
                    self.current += 1
                else:
                    raise Exception('Syntatic error (expecting semicolon after break or continue statement) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (unexpect argument in scopo) in line {}'.format(self.getCurrentToken().line))

        if((self.getCurrentToken().type not in total) and self.getCurrentToken().type != 'BCLOSE'):
            raise Exception('Syntatic error (unexpect argument in scopo) in line {}'.format(self.getCurrentToken().line))
        return

    # análise sintática para funções
    def funcStatement(self):
        aux = []
        aux.append("FUNC")
        self.flag = 1
        #Parametros de uma função só podem ser do tipo inteiro, boolean ou variável
        parameters = ["INTEGER", "BOOLEAN"]
        #Declaração de função através de palavra reservada
        if self.getCurrentToken().type == "FUNCTION":
            self.current += 1
            #Nome da função está em letra maiúscula?
            if str(self.getCurrentToken().lexeme).isupper() == True:
                aux.append(self.getCurrentToken().lexeme)
                aux.append(self.currentScope)
                aux.append(self.scopoPai)
                self.current += 1
                #Paranteses para passagem de parametros
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.current += 1
                    commaflag = False
                    #Leitura os parametros
                    while self.getCurrentToken().type != "PCLOSE":
                        #Parentese para passagem de parametros não foi fechado
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception('Syntatic error (expecting paranteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        #Declaração dos parametros
                        elif self.getCurrentToken().type in parameters:
                            #Identifica se há uma chamada de função ou procedure como parametro, que não é permitido
                            if self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getLookAheadToken().line))
                            #Identifica se há um identificador de tipagem para uma variável
                            elif self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == True:
                                aux.append("PAR")
                                aux.append("VAR")
                                aux.append(self.getCurrentToken().type)
                                aux.append(self.getLookAheadToken().lexeme)
                                aux.append(self.currentScope)
                                aux.append(self.scopoPai)
                                self.current += 2
                                commaflag = True
                            #Parametro válido
                            else:
                                #Leu um parametro sem que houvesse separação por virgulas
                                if(commaflag == True):
                                    raise Exception('Syntatic error (a comma was expected to be between two parameters) in line {}'.format(self.getCurrentToken().line))
                                self.current += 1
                                commaflag = True
                        #Lendo vírgula que separa os parametros
                        elif self.getCurrentToken().type == "COMMA" and commaflag == True:
                            if self.getLookAheadToken().type == "PCLOSE":
                               raise Exception('Syntatic error (expecting an argument after comma) in line{}'.format(self.getCurrentToken().line))
                            self.current += 1
                            commaflag = False
                        else:
                            raise Exception('Syntatic error (invalid function ou procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.symbols.append(aux)
                    aux.append(self.getCurrentToken().line)
                    self.symbolsSemantic.append(aux)
                    self.current += 1
                    #Declaração de {
                    if self.getCurrentToken().type == "BOPEN":
                        self.current += 1
                        #Se proximo token não for }, declaração de escopo
                        if self.getCurrentToken().type != "BCLOSE":
                            scopePaiAux = self.scopoPai
                            scopeAux = self.currentScope
                            self.scopoPai = self.currentScope
                            self.currentScope = self.newScope()
                            self.scopoStatement(0)
                            self.currentScope = scopeAux
                            self.scopoPai = scopePaiAux
                        #Função sem retorno definido
                        if self.flag == 1:
                            raise Exception('Syntatic error (function without return) in line {}'.format(self.getCurrentToken().line))
                        #Confere se a função fechou }
                        if self.getCurrentToken().type == "BCLOSE":
                            self.symbolsSemantic.append(["END FUNC"])
                            self.current += 1
                            return
                        else:
                            raise Exception('Syntatic error (expecting bracket at the end of the function scope) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception('Syntatic error (expecting bracket after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting parenteses after function label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (function label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (functions declaration must start with FUNCTION) in line{}'.format(self.getCurrentToken().line))

    # análise sintática para procedimentos
    def procStatement(self):
        aux = []
        parameters = ["INTEGER", "BOOLEAN", "LETTER", "NUM"]
        #Parametros de uma procedure só podem ser do tipo inteiro, boolean ou variável
        #Declaração de procedure através de palavra reservada
        if self.getCurrentToken().type == "PROCEDURE":
            aux.append("PROC")
            self.current += 1
            #Nome do procedure está em letra maiúscula?
            if str(self.getCurrentToken().lexeme).isupper() == True:
                aux.append(self.getCurrentToken().lexeme)
                aux.append(self.currentScope)
                aux.append(self.scopoPai)
                self.current += 1
                #Paranteses para passagem de parametros
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.current += 1
                    commaflag = False
                    #Leitura os parametros
                    while self.getCurrentToken().type != "PCLOSE":
                        #Parentese para passagem de parametros não foi fechado
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception('Syntatic error (expecting paranteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        #Declaração dos parametros
                        elif self.getCurrentToken().type in parameters:
                            #Identifica se há uma chamada de função ou procedure como parametro, que não é permitido
                            if self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getLookAheadToken().line))
                            #Identifica se há um identificador de tipagem para uma variável
                            elif self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == True:
                                aux.append("PAR")
                                aux.append("VAR")
                                aux.append(self.getCurrentToken().type)
                                aux.append(self.getLookAheadToken().lexeme)
                                aux.append(self.currentScope)
                                aux.append(self.scopoPai)
                                self.current += 2
                                commaflag = True
                            #Parametro válido
                            else:
                                #Leu um parametro sem que houvesse separação por virgulas
                                if(commaflag == True):
                                    raise Exception('Syntatic error (a comma was expected to be between two parameters) in line {}'.format(self.getCurrentToken().line))
                                self.current += 1
                                commaflag = True
                        #Lendo vírgula que separa os parametros
                        elif self.getCurrentToken().type == "COMMA" and commaflag == True:
                            if self.getLookAheadToken().type == "PCLOSE":
                               raise Exception('Syntatic error (expecting an argument after comma) in line{}'.format(self.getCurrentToken().line))
                            self.current += 1
                            commaflag = False
                        else:
                            raise Exception('Syntatic error (invalid function ou procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.symbols.append(aux)
                    aux.append(self.getCurrentToken().line)
                    self.symbolsSemantic.append(aux)
                    self.current += 1
                    #Declaração de {
                    if self.getCurrentToken().type == "BOPEN":
                        self.current += 1
                        #Se proximo token não for }, declaração de escopo
                        if self.getCurrentToken().type != "BCLOSE":
                            scopePaiAux = self.scopoPai
                            scopeAux = self.currentScope
                            self.scopoPai = self.currentScope
                            self.currentScope = self.newScope()
                            self.scopoStatement(1)
                            self.currentScope = scopeAux
                            self.scopoPai = scopePaiAux
                        #Confere se a função fechou }
                        if (self.getCurrentToken().type == "BCLOSE"):
                            self.symbolsSemantic.append(["END PROC"])
                            self.current += 1
                            return
                        else:
                            raise Exception('Syntatic error (expecting bracket at the end of procedure scope) in lin {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception('Syntatic error (expecting bracket after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting parenteses after procedure label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (procedure label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (procedure declaration must start with PROCEDURE) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamada de funções e procedimentos
    def callStatement(self):
        #Tipos que podem ser atribuidos aos parametros
        parameters = ["INTEGER", "BOOLEAN", "LETTER", "NUM"]
        if self.getCurrentToken().type == "LETTER":
            #Chamada de função ou procedure está em letra maiúscula
            if(self.getCurrentToken().lexeme.isupper() == True):
                StringSemantic = [self.getCurrentToken().lexeme]
                #Inserindo o escopo onde a chamada da função está
                scopoAux = self.getCurrentToken().lexeme+" "+str(self.currentScope)
                self.listScopos.append(scopoAux)
                #
                self.current += 1
                #Declaração dos parametros da chamada
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.current += 1
                    commaflag = False
                    #Leitura os parametros
                    while self.getCurrentToken().type != "PCLOSE":
                        #Parentese para passagem de parametros não foi fechado
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception('Syntatic error (expecting paranteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        #Declaração dos parametros
                        elif self.getCurrentToken().type in parameters:
                            #Identifica se há uma chamada de função ou procedure como parametro, que não é permitido
                            if self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getLookAheadToken().line))
                            #Identifica se há um identificador de tipagem para uma variável
                            elif self.getLookAheadToken().type == "LETTER" and self.getLookAheadToken().lexeme.islower() == True:
                                StringSemantic.append(self.getLookAheadToken().lexeme)
                                self.current += 2
                                commaflag = True
                            #Parametro válido
                            else:
                                #Leu um parametro sem que houvesse separação por virgulas
                                if(commaflag == True):
                                    raise Exception('Syntatic error (a comma was expected to be between two parameters) in line {}'.format(self.getCurrentToken().line))
                                StringSemantic.append(self.getCurrentToken().lexeme)
                                self.current += 1
                                commaflag = True
                        #Lendo vírgula que separa os parametros
                        elif self.getCurrentToken().type == "COMMA" and commaflag == True:
                            if self.getLookAheadToken().type == "PCLOSE":
                               raise Exception('Syntatic error (expecting an argument after comma) in line{}'.format(self.getCurrentToken().line))
                            self.current += 1
                            commaflag = False
                        else:
                            raise Exception('Syntatic error (invalid function ou procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                    #Validação do ; ao final da chamada de função ou procedure
                    if self.getCurrentToken().type == "SEMICOLON":
                        StringSemantic.append(self.getCurrentToken().line)
                        self.symbolsSemantic.append(StringSemantic)
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (expecting ; at the end of fucntion or procedure call) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntac error (expecting parenteses after function or procedure label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (functions and procedures must be in Upper case) in line {}'.format(self.getCurrentToken().line))
        #Chamada de função ou procedure sem ser com letter
        else:
            raise Exception('Syntatic error (invalid argument for function or procedure call) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamadas de sistema
    def systemCallStatement(self):
        #tipos de parametros válidos para System calls
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER", "NUM"]
        #Tipos de parametros inválidos para System calls
        cant = ["SEMICOLON", "END", "BOPEN", "BCLOSE"]
        #Declaração do IF
        if self.getCurrentToken().type == "IF":
            auxIF = ["IF"]
            self.current += 1
            #Validação do parantese para condição do IF
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                if(self.getCurrentToken().type == "PCLOSE"):
                    raise Exception('Syntatic error (expecting condition for IF) in line{}'.format(self.getCurrentToken().line)) 
                #Leitura da condição do IF
                while self.getCurrentToken().type != "PCLOSE":
                    #Não pode ler um token da proxima linha ou símbolo indevido pois implica que a condição do IF não foi finalizada
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception('Syntatic error (expecting parenteses after parameters scope) in line {}'.format(self.getCurrentToken().line))
                    #Chegagem da expressão presente no IF
                    else:
                        if(self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower() == False):
                            raise Exception('Syntatic error (invalid argument as parameter) in line{}'.format(self.getCurrentToken().line))
                        else:
                            self.checkExpression("BOOLEAN")
                            #pegar valor da expresão
                            auxExpression = self.expression
                            auxIF.append(auxExpression)
                            auxIF.append(self.getCurrentToken().line)
                            self.expression = ""
                self.symbolsSemantic.append(auxIF)
                self.current += 1
                #Abertura de Chaves = escopo do IF
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    #Declaração do escopo do IF
                    scopePaiAux = self.scopoPai
                    scopeAux = self.currentScope
                    self.scopoPai = self.currentScope
                    self.currentScope = self.newScope()
                    self.scopoStatement(1)
                    self.currentScope = scopeAux
                    self.scopoPai = scopePaiAux
                    #Declaração de encerramento do IF
                    if self.getCurrentToken().type == "BCLOSE":
                        self.symbolsSemantic.append(["END IF"])
                        #Declaração de IF e ELSE
                        if self.getLookAheadToken().type == "ELSE":
                            self.current += 2
                            self.symbolsSemantic.append(["ELSE"])
                            #Declaração do escopo do ELSE
                            if self.getCurrentToken().type == "BOPEN":
                                self.current += 1
                                scopePaiAux = self.scopoPai
                                scopeAux = self.currentScope
                                self.scopoPai = self.currentScope
                                self.currentScope = self.newScope()
                                self.scopoStatement(1)
                                self.currentScope = scopeAux
                                self.scopoPai = scopePaiAux
                                #Declaração do encerramento do ELSE
                                if self.getCurrentToken().type == "BCLOSE":
                                    self.symbolsSemantic.append(["END ELSE"])
                                    self.current += 1
                                    return
                                else:
                                    raise Exception('Syntatic error (expecting brackets after ELSE scope) in line {}'.format(self.getCurrentToken().line))

                            else:
                                raise Exception('Syntatic error (expecting brackets after ELSE) in line {}'.format(self.getCurrentToken().line))
                        #Declaração de IF sem ELSE
                        else:
                            self.current += 1
                            return
                    else:
                        raise Exception('Syntatic error (expecting brackets after IF scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting brackets after IF condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting parenteses after IF call) in line {}'.format(self.getCurrentToken().line))
            return

        #Declaração do While
        elif self.getCurrentToken().type == "WHILE":
            auxWHILE = ["WHILE"]
            self.current += 1
            #Declaração da condição do WHILE
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                if(self.getCurrentToken().type == "PCLOSE"):
                    raise Exception('Syntatic error (expecting condition for WHILE) in line{}'.format(self.getCurrentToken().line))
                #Leitura da condição do WHILE
                while self.getCurrentToken().type != "PCLOSE":
                    #Não pode ler um token da proxima linha ou símbolo indevido pois implica que a condição do WHILE não foi finalizada
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception('Syntatic error (expecting paranteses after WHILE condition) in line {}'.format(self.getCurrentToken().line))
                    #Leitura da expressão condicional
                    #Chegagem da expressão presente no IF
                    else:
                        if(self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower() == False):
                            raise Exception('Syntatic error (invalid argument as parameter) in line{}'.format(self.getCurrentToken().line))
                        else:
                            self.checkExpression("BOOLEAN")
                            #pega valor da expressão
                            auxExpression = self.expression
                            auxWHILE.append(auxExpression)
                            auxWHILE.append(self.getCurrentToken().line)
                            self.expression = ""
                self.symbolsSemantic.append(auxWHILE)
                self.current += 1
                #Declaração do escopo do WHILE
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    scopePaiAux = self.scopoPai
                    scopeAux = self.currentScope
                    self.scopoPai = self.currentScope
                    self.currentScope = self.newScope()
                    self.scopoStatement(2)
                    self.currentScope = scopeAux
                    self.scopoPai = scopePaiAux
                    if self.getCurrentToken().type == "BREAK" or self.getCurrentToken().type == "CONTINUE":
                        if(self.getLookAheadToken().type == "SEMICOLON"):
                            self.current+=2
                        else:
                            raise Exception('Syntatic error (expecting semicolon after a break or continue statement) in line {}'.format(self.getCurrentToken().line))
                    #Declaração de termino do WHILE
                    if self.getCurrentToken().type == "BCLOSE":
                        self.symbolsSemantic.append(["END WHILE"])
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (expecting brackets after WHILE scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting brackets after WHILE condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting parenteses after WHILE call) in line {}'.format(self.getCurrentToken().line))
            return

        #Declaração PRINT
        elif self.getCurrentToken().type == "PRINT":
            StringSemantic = ["PRINT"]
            #Inserindo o escopo onde a chamada da função está
            scopoAux = self.getCurrentToken().lexeme
            #
            self.current += 1
            #Declaração de parametros do PRINT
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                if(self.getCurrentToken().type == "PCLOSE"):
                    raise Exception('Syntatic error (expecting argument for PRINT) in line{}'.format(self.getCurrentToken().line))
                #Leitura dos parametros do PRINT
                while self.getCurrentToken().type != "PCLOSE":
                    #Não pode ler um token da proxima linha ou símbolo indevido pois implica que o PRINT não foi finalizado
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception('Syntatic error (expecting paranteses after PRINT statements) in line {}'.formar(self.getCurrentToken().line))
                    #Chegagem da expressão presente no IF
                    else:
                        if(self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower() == False):
                            raise Exception('Syntatic error (invalid argument as parameter) in line{}'.format(self.getCurrentToken().line))
                        #Elemento permitido no print
                        elif(self.getCurrentToken().type in parameters):
                            if(self.getCurrentToken().type != "COMMA"):
                                StringSemantic.append(self.getCurrentToken().lexeme)
                            scopoAux += " "+self.getCurrentToken().lexeme
                            self.current += 1
                        else:
                            raise Exception('Syntatic error (invalid argument as parameter) in line{}'.format(self.getCurrentToken().line))
                self.current += 1
                #Declaração de ; após o PRINT
                if self.getCurrentToken().type == "SEMICOLON":
                    StringSemantic.append(self.getCurrentToken().line)
                    self.symbolsSemantic.append(StringSemantic)
                    scopoAux +=", "+str(self.currentScope)
                    scopoAux +=", "+str(self.scopoPai)
                    self.listScopos.append(scopoAux)
                    self.current += 1
                    return
                else:
                    raise Exception('Syntatic error (expecting ; after PRINT call) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting parenteses after PRINT) in line {}'.format(self.getCurrentToken().line))

        #Declaração do RETURN
        elif self.getCurrentToken().type == "RETURN":
            aux = []
            aux.append(self.getCurrentToken().type)
            self.current += 1
            #Tipos válidos de retorno
            parameters = ["INTEGER", "BOOLEAN", "LETTER", "NUM"]
            #Declaração do tipo do retorno
            if self.getCurrentToken().type in parameters:
                #Checar retorno de variável
                if self.getCurrentToken().type == "LETTER":
                    #Chegagem de chamada de procedure ou chamda de função, incluindo recursão, não é válida
                    if self.getCurrentToken().lexeme.islower() == False:
                        raise Exception('Syntatic error (invalid argument for RETURN) in line {}'.format(self.getCurrentToken().line))
                    #Retorno válido
                    else:
                        aux.append(self.searchSymbolTable(self.getCurrentToken().lexeme,self.currentScope,self.scopoPai))
                        aux.append(self.getCurrentToken().lexeme)
                        aux.append(self.currentScope)
                        aux.append(self.scopoPai)
                        self.current += 1
                        #Declaração de ; após o return
                        if self.getCurrentToken().type == "SEMICOLON":
                            linha = self.getCurrentToken().line
                            self.current += 1
                            self.flag = 0
                            self.symbols.append(aux)
                            aux.append(linha)
                            self.symbolsSemantic.append(aux)
                            return
                        else:
                            raise Exception('Syntatic error (expecting ; but recieved invalid argument) in line {}'.format(self.getCurrentToken().line))
                #checar retorno de valor bruto
                else:
                    if(self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN" or self.getCurrentToken().type == "NUM"):
                        aux.append(self.getCurrentToken().type)
                        aux.append(self.getCurrentToken().lexeme)
                        aux.append(self.currentScope)
                        aux.append(self.scopoPai)
                        self.current += 1
                        #Declaração de ; após o return
                        if self.getCurrentToken().type == "SEMICOLON":
                            self.current += 1
                            self.flag = 0
                            self.symbols.append(aux)
                            aux.append(self.getCurrentToken().line)
                            self.symbolsSemantic.append(aux)
                            return
                        else:
                            raise Exception('Syntatic error (expecting ; but recieved invalid argument) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception('Syntatic error (invalid return value) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (invalid type as return) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (unexpect argument of system call) in line {}'.format(self.getCurrentToken().line))


    def searchSymbolTable(self,query, scope, scopoPai):
        flag = False
        retorno = ""
        for i in range(len(self.symbols)):
            aux = self.symbols[i]
            if(aux[2] == query and aux[5] == scope):
                flag = True;
                retorno = aux[1]
                break
            elif(aux[0] == "FUNC"):
                for j in range(len(aux)-1):
                    if(aux[j] == query and aux[j+1] == scopoPai):
                        flag = True
                        retorno = aux[j-1]
                        break
                if(flag):
                    break
        if(flag):
            return retorno
        else:
            raise Exception('Returning an undeclared variable in line {}'.format(self.getCurrentToken().line))

    def newScope(self):
        newscope = self.scopes[len(self.scopes)-1]+1
        self.scopes.append(newscope)
        return newscope
