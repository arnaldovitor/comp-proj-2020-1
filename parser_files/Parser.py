from parser_files.Util import *

class Parser():
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens
        self.error = False

    def getCurrentToken(self):
        return self.tokens[self.current]

    def getLookAheadToken(self):
        return self.tokens[self.current + 1]

    def start(self):
        self.statementList()
        return

    def statementList(self):
        if self.getCurrentToken().type == "END":
            return
        else:
            self.statement()
            self.statementList()
            return

    def statement(self):
        systemcalls = ["IF","WHILE","PRINT"]
        if self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN":
            self.varStatement()
            return
        elif self.getCurrentToken().type == "FUNCTION":
            self.funcStatement()
            return
        elif self.getCurrentToken().type == "LETTER":
            self.callStatement()
            return
        elif self.getCurrentToken().type in systemcalls:
            self.systemCallStatement()
            return

    # análise sintática para cadeia de tokens que começam com INTEGER ou BOOLEAN
    def varStatement(self):
        self.current += 1
        if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower():
            self.current += 1
            if self.getCurrentToken().type == "ATTR":
                self.current += 1
                self.checkExpression()
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current += 1
                    return
                else:
                    self.error = True
                    raise Exception('Syntatic error (need ;) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para expressões lógicas ou aritméticas
    def checkExpression(self):
        print(self.getCurrentToken().type)
        if self.getCurrentToken().type == "NUM":
            # passa casos do tipo INTEGER x = NUMBER;
            if hasLogicSymbol(self.getLookAheadToken()) == False:
                if hasArithmeticSymbol(self.getLookAheadToken()) == False:
                    self.current += 1
                    return
                else:
                    # passa casos do tipo INTEGER x = NUMBER + NUMBER;
                    self.current += 1
                    if self.getLookAheadToken().type == "NUM" or self.getLookAheadToken().type == "LETTER":
                        self.current += 2
                        return
                    else:
                        #nega casos do tip INTEGER x = NUMBER + *;
                        self.error = True
                        raise Exception('Syntatic error (arithmetic expression) in line {}'.format(self.getCurrentToken().line))


    # análise sintática de escopo
    def scopoStatement(self):
        total = ["SEMICOLON","LETTER","IF","WHILE","PRINT","INTEGER","BOOLEAN"]
        parameters = ["INTEGER","BOOLEAN","LETTER"]
        systemcalls = ["IF","WHILE","PRINT"]
        while(self.getLookAheadToken().type in total):
            if(self.getCurrentToken().type in systemcalls):
                self.systemCallStatement()
            elif(self.getCurrentToken().type in parameters):
                if(self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True):
                   self.callStatement()
                else:
                    self.varStatement()
            elif(self.getCurrentToken().type == "SEMICOLON"):
                print(self.getCurrentToken())
                self.current += 1
            else:
                raise Exception ('Syntatic error (unexpect argument in scopo) in line {}'.format(self.getCurrentToken().line))
        return
    
    # análise sintática para funções
    def funcStatement(self):
        parameters = ["INTEGER","BOOLEAN","COMMA","LETTER"]
        print(self.getCurrentToken())
        if self.getCurrentToken().type == "FUNCTION":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                print(self.getCurrentToken())
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    print(self.getCurrentToken())
                    self.current += 1
                    while(self.getCurrentToken().type != "PCLOSE"):
                        if self.getCurrentToken().type in parameters:
                            print(self.getCurrentToken())
                            self.current += 1
                        else:
                            raise Exception ('Syntatic error (invalid function parameter) in line {}'.format(self.getCurrentToken().line))
                    print(self.getCurrentToken())
                    self.current += 1
                    if(self.getCurrentToken().type == "BOPEN"):
                        print(self.getCurrentToken())
                        self.current += 1
                        if(self.getCurrentToken().type != "RETURN"):
                            self.scopoStatement()
                            self.current += 1
                        print(self.getCurrentToken())
                        self.current += 1
                        if(self.getCurrentToken().type in parameters):
                            print(self.getCurrentToken())
                            self.current += 1
                            if(self.getCurrentToken().type == "BCLOSE"):
                                print(self.getCurrentToken())
                                self.current += 1
                                return
                            else:
                                raise Exception ('Syntatic error (expecting } at the end of the function scope) in line {}'.format(self.getCurrentToken().line))
                        else:
                            raise Exception ('Syntatic error (invalid return of function) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception ('Syntatic error (expecting { after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception ('Syntatic error (expecting ( after function label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception ('Syntatic error (function label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception ('Syntatic error (functions declaration must start with FUNCTION) in line{}'.format(self.getCurrentToken().line))
        
    # análise sintática para procedimentos
    def procStatement(self):
        parameters = ["INTEGER","BOOLEAN","COMMA","LETTER"]
        print(self.getCurrentToken())
        if self.getCurrentToken().type == "PROCEDURE":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                print(self.getCurrentToken())
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    print(self.getCurrentToken())
                    self.current += 1
                    while(self.getCurrentToken().type != "PCLOSE"):
                        if self.getCurrentToken().type in parameters:
                            print(self.getCurrentToken())
                            self.current += 1
                        else:
                            raise Exception ('Syntatic error (invalid procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    print(self.getCurrentToken())
                    self.current += 1
                    if(self.getCurrentToken().type == "BOPEN"):
                        print(self.getCurrentToken())
                        self.current += 1
                        if(self.getCurrentToken().type != "BCLOSE"):
                            self.scopoStatement()
                            self.current += 1
                        print(self.getCurrentToken())
                        self.current += 1
                    else:
                        raise Exception ('Syntatic error (expecting { after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception ('Syntatic error (expecting ( after procedure label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception ('Syntatic error (procedure label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception ('Syntatic error (procedure declaration must start with PROCEDURE) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamada de funções e procedimentos
    def callStatement(self):
        parameters = ["INTEGER","BOOLEAN","COMMA","LETTER","NUM"]
        print(self.getCurrentToken())
        if self.getCurrentToken().type == "LETTER":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                print(self.getCurrentToken())
                self.current+=1
                while(self.getCurrentToken().type != "PCLOSE"):
                    if(self.getCurrentToken().type in parameters):
                        print(self.getCurrentToken())
                        self.current += 1
                    else:
                        raise Exception ('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                print(self.getCurrentToken())
                self.current += 1
                if(self.getCurrentToken().type == "SEMICOLON"):
                    print(self.getCurrentToken())
                    self.current += 1
                else:
                    raise Exception ('Syntatic error (expecting ; at the end of fucntion or procedure call) in line {}'.format(self.getCurrentToken.line))
            else:
                raise Exception ('Syntac error (expecting ( after function or procedure label) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception ('Syntatic error (unexpect argument for function or procedure call) in line {}'.format(self.getCurrentToken().line))
        
    # análise sintática para chamadas de sistema
    def systemCallStatement(self):
        parameters = ["INTEGER","BOOLEAN","COMMA","LETTER","NUM"]
        print(self.getCurrentToken())
        if(self.getCurrentToken().type == "IF"):
            self.current+=1
            if self.getCurrentToken().type == "POPEN":
                print(self.getCurrentToken())
                self.current += 1
                while(self.getCurrentToken().type != "PCLOSE"):
                    self.checkExpression()
                print(self.getCurrentToken())
                self.current += 1
                if (self.getCurrentToken().type == "BOPEN"):
                    print(self.getCurrentToken())
                    self.current += 1
                    self.scopoStatement()
                    print(self.getCurrentToken())
                    self.current += 1
                    if(self.getCurrentToken().type == "BCLOSE"):
                        if(self.getLookAheadToken().type == "ELSE"):
                            print(self.getLookAheadToken())
                            self.current += 2
                            if(self.getCurrentToken().type == "BOPEN"):
                                print(self.getCurrentToken())
                                self.current += 1
                                self.scopoStatement()
                                print(self.getCurrentToken())
                                self.current += 1
                                if(self.getCurrentToken().type == "BCLOSE"):
                                    print(self.getCurrentToken())
                                    self.current += 1
                                    return
                                else:
                                    raise Exception ('Syntatic error (expecting } after ELSE scope) in line {}'.format(self.getCurrentToken().line))
                
                            else:
                                raise Exception ('Syntatic error (expecting { after ELSE) in line {}'.format(self.getCurrentToken().line))
                        else:
                            return
                    else:
                        raise Exception ('Syntatic error (expecting } after IF scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception ('Syntatic error (expecting { after IF condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception ('Syntatic error (expecting ( after IF call) in line {}'.format(self.getCurrentToken().line))
            return
            
        elif(self.getCurrentToken().type == "WHILE"):
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                print(self.getCurrentToken())
                self.current += 1
                while(self.getCurrentToken().type != "PCLOSE"):
                    self.checkExpression()
                print(self.getCurrentToken())
                self.current += 1
                if (self.getCurrentToken().type == "BOPEN"):
                    print(self.getCurrentToken())
                    self.current += 1
                    self.scopoStatement()
                    print(self.getCurrentToken())
                    self.current += 1
                    if(self.getCurrentToken().type == "BCLOSE"):
                        print(self.getCurrentToken())
                        self.current += 1
                    else:
                        raise Exception ('Syntatic error (expecting } after WHILE scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception ('Syntatic error (expecting { after WHILE condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception ('Syntatic error (expecting ( after WHILE call) in line {}'.format(self.getCurrentToken().line))
            return

        elif(self.getCurrentToken().type == "PRINT"):
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                print(self.getCurrentToken())
                self.current += 1
                while(self.getCurrentToken().type != "PCLOSE"):
                    if self.getCurrentToken().type in parameters:
                        if(self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True):
                            self.callStatement()
                        else:
                            print(self.getCurrentToken())
                            self.current += 1
                    else:
                        raise Exception ('Syntatic error (invalide argument after as parameter) in line {}'.format(self.getCurrentToken().line))
                print(self.getCurrentToken())
                self.current += 1
                if(self.getCurrentToken().type == "SEMICOLON"):
                    print(self.getCurrentToken())
                    self.current += 1
                else:
                    raise Exception ('Syntatic error (expecting ; after PRINT call) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception ('Syntatic error (expecting ( after PRINT) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception ('Syntatic error (unexpect argument of system call) in line {}'.format(self.getCurrentToken().line))
