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
        systemCalls = ["IF", "WHILE", "PRINT"]
        if self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN":
            self.varStatement()
            return
        elif self.getCurrentToken().type == "FUNCTION":
            self.funcStatement()
            return
        elif self.getCurrentToken().type == "LETTER":
            self.callStatement()
            return
        elif self.getCurrentToken().type in systemCalls:
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
                    raise Exception('Syntatic error (expecting ; after variable declaration) in line {}'.format(self.getCurrentToken().line))
            else:
                self.error = True
                raise Exception('Syntatic error (expecting = in variable declaration) in line {}'.format(self.getCurrentToken().line))
        else:
            self.error = True
            raise Exception('Syntatic error (expecting a variable name) in line {}'.formart(self.getCurrentToken().line))

    # análise sintática para expressões lógicas ou aritméticas
    def checkExpression(self):
        if self.getCurrentToken().type == "NUM":
            # passa para declaração simples de integer
            if hasLogicSymbol(self.getLookAheadToken()) == False:
                if hasArithmeticSymbol(self.getLookAheadToken()) == False:
                    self.current += 1
                    return
                else:
                    # passa casos do tipo num + num
                    self.current += 1
                    if self.getLookAheadToken().type == "NUM" or self.getLookAheadToken().type == "LETTER":
                        self.current += 2
                        return
                    else:
                        #nega casos num + /
                        self.error = True
                        raise Exception('Syntatic error (arithmetic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                # casos que tem expressões lógicas
                self.current += 1
                # passa para casos como num > num
                if self.getLookAheadToken().type == "NUMBER":
                    pass
                # passa para casos como num > var
                elif self.getLookAheadToken().type == "LETTER":
                    if self.getLookAheadToken().lexema.islower():
                        self.current += 2
                        return
                    # passa para casos como num > function()
                    elif self.getLookAheadToken().lexema.isupper():
                        self.current += 2
                        if self.getCurrentToken().type == "POPEN":
                            self.current += 1
                            while self.getCurrentToken().type != "PCLOSE":
                                if self.getCurrentToken().type == "NUM" or self.getCurrentToken().type == "BOOLEAN" or self.getLookAheadToken().lexema.islower():
                                    self.current += 1
                                    if self.getCurrentToken().type == "COMMA":
                                        self.current += 1
                                        if self.getCurrentToken().type == "PCLOSE":
                                            self.error = True
                                            raise Exception('Syntatic error (more arguments needed) in line {}'.format(self.getCurrentToken().line))
                                    elif self.getCurrentToken().type == "PCLOSE":
                                        self.current += 1
                                        break
                                    else:
                                        self.error = True
                                        raise Exception('Syntatic error (unexpect comma) in line {}'.format(self.getCurrentToken().line))
                                else:
                                    self.error = True
                                    raise Exception('Syntatic error (invalid argument) in line {}'.format(self.getCurrentToken().line))
                        else:
                            self.error = True
                            raise Exception('Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
                    else:
                        self.error = True
                        raise Exception('Syntatic error (expecting operation with function or variable) in line {}'.format(self.getCurrentToken().line))
                else:
                    self.error = True
                    raise Exception('Syntatic error (expecting a logical expression) in line {}'.format(self.getCurrentToken().line))
        elif self.getCurrentToken().type == "LETTER":
            # declaração de var recebendo function
            if self.getCurrentToken().lexeme.isupper():
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    self.current += 1
                    while self.getCurrentToken() != "PCLOSE":
                        if self.getCurrentToken().type == "NUM" or self.getCurrentToken().type == "BOOLEAN" or self.getCurrentToken().lexeme.islower:
                            self.current += 1
                            if self.getCurrentToken().type == "COMMA":
                                self.current += 1
                                if self.getCurrentToken().type == "PCLOSE":
                                    self.error = True
                                    raise Exception('Syntatic error (more arguments needed) in line {}'.format(self.getCurrentToken().line))
                            elif self.getCurrentToken().type == "PCLOSE":
                                break
                            else:
                                self.error = True
                                raise Exception('Syntatic error (unexpect comma) in line {}'.format(self.getCurrentToken().line))
                        else:
                            self.error = True
                            raise Exception('Syntatic error (invalid argument) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                else:
                    self.error = True
                    raise Exception('Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
            # PROBLEMAS AQUI (?)
            elif self.getCurrentToken().lexeme.islower():
                if hasLogicSymbol(self.getLookAheadToken()) or hasArithmeticSymbol(self.getLookAheadToken()):
                    self.current += 3
                    return
                else:
                    self.error = True
                    raise Exception('Syntatic error (incomplete logic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                self.error = True
                raise Exception('Syntatic error (expecting function name is upper or variable name is lower in line {}'.format(self.getCurrentToken().line))

        elif self.getCurrentToken().type == "BOOLEAN":
            self.current += 1

        else:
            self.error = True
            raise Exception('Syntatic error expression in line {}'.format(self.getCurrentToken().line))

    # análise sintática de escopo
    def scopoStatement(self):
        total = ["SEMICOLON", "LETTER", "IF", "WHILE", "PRINT", "INTEGER", "BOOLEAN"]
        parameters = ["INTEGER", "BOOLEAN", "LETTER"]
        systemCalls = ["IF", "WHILE", "PRINT"]
        while self.getLookAheadToken().type in total:
            if self.getCurrentToken().type in systemCalls:
                self.systemCallStatement()
            elif self.getCurrentToken().type in parameters:
                if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True:
                   self.callStatement()
                else:
                    self.varStatement()
            elif self.getCurrentToken().type == "SEMICOLON":
                self.current += 1
            else:
                raise Exception('Syntatic error (unexpect argument in scopo) in line {}'.format(self.getCurrentToken().line))
        return

    # análise sintática para funções
    def funcStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER"]
        if self.getCurrentToken().type == "FUNCTION":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    self.current += 1
                    while self.getCurrentToken().type != "PCLOSE":
                        if self.getCurrentToken().type in parameters:
                            self.current += 1
                        else:
                            raise Exception('Syntatic error (invalid function parameter) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                    if self.getCurrentToken().type == "BOPEN":
                        self.current += 1
                        if self.getCurrentToken().type != "RETURN":
                            self.scopoStatement()
                            self.current += 1
                        self.current += 1
                        if self.getCurrentToken().type in parameters:
                            self.current += 1
                            if self.getCurrentToken().type == "BCLOSE":
                                self.current += 1
                                return
                            else:
                                raise Exception('Syntatic error (expecting } at the end of the function scope) in line {}'.format(self.getCurrentToken().line))
                        else:
                            raise Exception('Syntatic error (invalid return of function) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception('Syntatic error (expecting { after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting ( after function label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (function label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (functions declaration must start with FUNCTION) in line{}'.format(self.getCurrentToken().line))

    # análise sintática para procedimentos
    def procStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER"]
        if self.getCurrentToken().type == "PROCEDURE":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    self.current += 1
                    while self.getCurrentToken().type != "PCLOSE":
                        if self.getCurrentToken().type in parameters:
                            self.current += 1
                        else:
                            raise Exception('Syntatic error (invalid procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                    if self.getCurrentToken().type == "BOPEN":
                        self.current += 1
                        if self.getCurrentToken().type != "BCLOSE":
                            self.scopoStatement()
                            self.current += 1
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (expecting { after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting ( after procedure label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (procedure label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (procedure declaration must start with PROCEDURE) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamada de funções e procedimentos
    def callStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER", "NUM"]
        if self.getCurrentToken().type == "LETTER":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().type in parameters:
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                self.current += 1
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current += 1
                else:
                    raise Exception('Syntatic error (expecting ; at the end of fucntion or procedure call) in line {}'.format(self.getCurrentToken.line))
            else:
                raise Exception('Syntac error (expecting ( after function or procedure label) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (unexpect argument for function or procedure call) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamadas de sistema
    def systemCallStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER", "NUM"]
        if self.getCurrentToken().type == "IF":
            self.current+=1
            if self.getCurrentToken().type == "POPEN":
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    self.checkExpression()
                self.current += 1
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    self.scopoStatement()
                    self.current += 1
                    if self.getCurrentToken().type == "BCLOSE":
                        if self.getLookAheadToken().type == "ELSE":
                            self.current += 2
                            if self.getCurrentToken().type == "BOPEN":
                                self.current += 1
                                self.scopoStatement()
                                self.current += 1
                                if self.getCurrentToken().type == "BCLOSE":
                                    self.current += 1
                                    return
                                else:
                                    raise Exception('Syntatic error (expecting } after ELSE scope) in line {}'.format(self.getCurrentToken().line))

                            else:
                                raise Exception('Syntatic error (expecting { after ELSE) in line {}'.format(self.getCurrentToken().line))
                        else:
                            return
                    else:
                        raise Exception('Syntatic error (expecting } after IF scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting { after IF condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting ( after IF call) in line {}'.format(self.getCurrentToken().line))
            return

        elif self.getCurrentToken().type == "WHILE":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    self.checkExpression()
                self.current += 1
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    self.scopoStatement()
                    self.current += 1
                    if self.getCurrentToken().type == "BCLOSE":
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (expecting } after WHILE scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting { after WHILE condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting ( after WHILE call) in line {}'.format(self.getCurrentToken().line))
            return

        elif self.getCurrentToken().type == "PRINT":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().type in parameters:
                        if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True:
                            self.callStatement()
                        else:
                            self.current += 1
                    else:
                        raise Exception('Syntatic error (invalide argument after as parameter) in line {}'.format(self.getCurrentToken().line))
                self.current += 1
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current += 1
                else:
                    raise Exception('Syntatic error (expecting ; after PRINT call) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting ( after PRINT) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (unexpect argument of system call) in line {}'.format(self.getCurrentToken().line))
