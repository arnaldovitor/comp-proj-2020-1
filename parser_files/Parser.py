from parser_files.Util import *


class Parser():
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens
        self.flag = 0

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
        systemCalls = ["IF", "WHILE", "PRINT", "RETURN"]
        if self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN":
            self.varStatement()
            return
        elif self.getCurrentToken().type == "FUNCTION":
            self.funcStatement()
            return
        elif self.getCurrentToken().type == "PROCEDURE":
            self.procStatement()
            return
        elif self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.isupper() == True:
            self.callStatement()
            return
        elif self.getCurrentToken().type in systemCalls:
            self.systemCallStatement()
            return
        else:
            raise Exception('Syntatic error (variable initialized without type) in line{}'.format(self.getCurrentToken().line))

    # análise sintática para cadeia de tokens que começam com INTEGER ou BOOLEAN
    def varStatement(self):
        self.current += 1
        if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower():
            self.current += 1
            if self.getCurrentToken().type == "ATTR":
                self.current += 1
                line = self.getCurrentToken().line
                self.checkExpression()
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current += 1
                    return
                elif self.getCurrentToken().line == line and self.getCurrentToken().type != "END":
                    raise Exception(
                        'Syntatic error (expressions must be at most between two operands) in line{}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting ; after variable declaration) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting = in variable declaration) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (expecting a variable name) in line {}'.format(self.getCurrentToken().line))

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
                        # nega casos num + /
                        raise Exception(
                            'Syntatic error (arithmetic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                # casos que tem expressões lógicas
                self.current += 1
                # passa para casos como num > num
                if self.getLookAheadToken().type == "NUM":
                    self.current += 2
                    return
                # passa para casos como num > var
                elif self.getLookAheadToken().type == "LETTER":
                    if self.getLookAheadToken().lexeme.islower():
                        self.current += 2
                        return
                    # passa para casos como num > function()
                    elif self.getLookAheadToken().lexeme.isupper():
                        self.current += 2
                        if self.getCurrentToken().type == "POPEN":
                            self.current += 1
                            while self.getCurrentToken().type != "PCLOSE":
                                if self.getCurrentToken().type == "NUM" or self.getCurrentToken().type == "BOOLEAN" or self.getLookAheadToken().lexema.islower():
                                    self.current += 1
                                    if self.getCurrentToken().type == "COMMA":
                                        self.current += 1
                                        if self.getCurrentToken().type == "PCLOSE":
                                            raise Exception('Syntatic error (more arguments needed) in line {}'.format(self.getCurrentToken().line))
                                    elif self.getCurrentToken().type == "PCLOSE":
                                        self.current += 1
                                        break
                                    else:
                                        raise Exception('Syntatic error (unexpect comma) in line {}'.format(self.getCurrentToken().line))
                                else:
                                    raise Exception('Syntatic error (invalid argument) in line {}'.format(self.getCurrentToken().line))
                        else:
                            raise Exception(
                                'Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception(
                            'Syntatic error (expecting operation with function or variable) in line {}'.format(self.getCurrentToken().line))
                else:
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
                                    raise Exception('Syntatic error (more arguments needed) in line {}'.format(self.getCurrentToken().line))
                            elif self.getCurrentToken().type == "PCLOSE":
                                break
                            else:
                                raise Exception(
                                    'Syntatic error (unexpect comma) in line {}'.format(self.getCurrentToken().line))
                        else:
                            raise Exception(
                                'Syntatic error (invalid argument) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                else:
                    raise Exception(
                        'Syntatic error (expecting parentheses) in line {}'.format(self.getCurrentToken().line))
            elif self.getCurrentToken().lexeme.islower():
                if hasLogicSymbol(self.getLookAheadToken()) or hasArithmeticSymbol(self.getLookAheadToken()):
                    self.current += 3
                    return
                else:
                    raise Exception(
                        'Syntatic error (incomplete logic expression) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception(
                    'Syntatic error (expecting function name is upper or variable name is lower in line {}'.format(self.getCurrentToken().line))

        elif self.getCurrentToken().type == "BOOLEAN":
            self.current += 1

        else:
            raise Exception('Syntatic error expression in line {}'.format(self.getCurrentToken().line))

    # análise sintática de escopo
    def scopoStatement(self):
        total = ["SEMICOLON", "LETTER", "IF", "WHILE", "PRINT", "INTEGER", "BOOLEAN", "RETURN"]
        parameters = ["INTEGER", "BOOLEAN", "LETTER"]
        systemCalls = ["IF", "WHILE", "PRINT", "RETURN"]
        while self.getCurrentToken().type in total:
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
                raise Exception(
                    'Syntatic error (unexpect argument in scopo) in line {}'.format(self.getCurrentToken().line))
        return

    # análise sintática para funções
    def funcStatement(self):
        self.flag = 1
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER"]
        if self.getCurrentToken().type == "FUNCTION":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.current += 1
                    while self.getCurrentToken().type != "PCLOSE":
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception(
                                'Syntatic error (expecting paranteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        elif self.getCurrentToken().type in parameters:
                            if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                            else:
                                self.current += 1
                        else:
                            raise Exception('Syntatic error (invalid function parameter) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                    if self.getCurrentToken().type == "BOPEN":
                        self.current += 1
                        if self.getCurrentToken().type != "BCLOSE":
                            self.scopoStatement()
                        if self.flag == 1:
                            raise Exception('Syntatic error (function without return) in line {}'.format(self.getCurrentToken().line))
                        if self.getCurrentToken().type == "BCLOSE":
                            self.current += 1
                            return
                        else:
                            raise Exception(
                                'Syntatic error (expecting bracket at the end of the function scope) in line {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception(
                            'Syntatic error (expecting bracket after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting parenteses after function label) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (function label must be in upper letters) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (functions declaration must start with FUNCTION) in line{}'.format(self.getCurrentToken().line))

    # análise sintática para procedimentos
    def procStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "LETTER", "COMMA"]
        if self.getCurrentToken().type == "PROCEDURE":
            self.current += 1
            if str(self.getCurrentToken().lexeme).isupper() == True:
                self.current += 1
                if self.getCurrentToken().type == "POPEN":
                    line = self.getCurrentToken().line
                    self.current += 1
                    while self.getCurrentToken().type != "PCLOSE":
                        if self.getCurrentToken().line != line or self.getCurrentToken().type == "BOPEN" or self.getCurrentToken().type == "END":
                            raise Exception(
                                'Syntatic error (expecting parenteses after parameters definition) in line {}'.format(self.getCurrentToken().line))
                        elif self.getCurrentToken().type in parameters:
                            if self.getCurrentToken().type == "LETTER" and self.getCurrentToken.lexeme.islower() == False:
                                raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                            else:
                                self.current += 1
                        else:
                            raise Exception('Syntatic error (invalid procedure parameter) in line {}'.format(self.getCurrentToken().line))
                    self.current += 1
                    if self.getCurrentToken().type == "BOPEN":

                        self.current += 1
                        self.scopoStatement()
                        if (self.getCurrentToken().type == "BCLOSE"):
                            self.current += 1
                            return
                        else:
                            raise Exception(
                                'Syntatic error (expecting bracket at the end of procedure scope) in lin {}'.format(self.getCurrentToken().line))
                    else:
                        raise Exception(
                            'Syntatic error (expecting bracket after parameters definition) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting parenteses after procedure label) in line {}'.format(self.getCurrentToken().line))
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
                line = self.getCurrentToken().line
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().line != line or self.getCurrentToken().type == "SEMICOLON" or self.getCurrentToken().type == "END":
                        raise Exception(
                            'Syntatic error (expecting parenteses after parameters scope) in line {}'.format(self.getCurrentToken().line))
                    elif self.getCurrentToken().type in parameters:
                        if (
                                self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower() == False):
                            raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                        else:
                            self.current += 1
                    else:
                        raise Exception('Syntatic error (invalid argument as parameter) in line {}'.format(self.getCurrentToken().line))
                self.current += 1
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current += 1
                else:
                    raise Exception(
                        'Syntatic error (expecting ; at the end of fucntion or procedure call) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception(
                    'Syntac error (expecting parenteses after function or procedure label) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception('Syntatic error (unexpect argument for function or procedure call) in line {}'.format(self.getCurrentToken().line))

    # análise sintática para chamadas de sistema
    def systemCallStatement(self):
        parameters = ["INTEGER", "BOOLEAN", "COMMA", "LETTER", "NUM"]
        cant = ["SEMICOLON", "END", "BOPEN", "BCLOSE"]
        if self.getCurrentToken().type == "IF":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception(
                            'Syntatic error (expecting parenteses after parameters scope) in line {}'.format(self.getCurrentToken().line))
                    else:
                        self.checkExpression()
                self.current += 1
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    self.scopoStatement()
                    if self.getCurrentToken().type == "BCLOSE":
                        if self.getLookAheadToken().type == "ELSE":
                            self.current += 2
                            if self.getCurrentToken().type == "BOPEN":
                                self.current += 1
                                self.scopoStatement()
                                if self.getCurrentToken().type == "BCLOSE":
                                    self.current += 1
                                    return
                                else:
                                    raise Exception(
                                        'Syntatic error (expecting brackets after ELSE scope) in line {}'.format(self.getCurrentToken().line))

                            else:
                                raise Exception('Syntatic error (expecting brackets after ELSE) in line {}'.format(self.getCurrentToken().line))
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

        elif self.getCurrentToken().type == "WHILE":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception('Syntatic error (expecting paranteses after WHILE condition) in line {}'.format(self.getCurrentToken().line))
                    self.checkExpression()
                self.current += 1
                if self.getCurrentToken().type == "BOPEN":
                    self.current += 1
                    self.scopoStatement()
                    if self.getCurrentToken().type == "BCLOSE":
                        self.current += 1
                    else:
                        raise Exception('Syntatic error (expecting brackets after WHILE scope) in line {}'.format(self.getCurrentToken().line))
                else:
                    raise Exception('Syntatic error (expecting brackets after WHILE condition) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception('Syntatic error (expecting parenteses after WHILE call) in line {}'.format(self.getCurrentToken().line))
            return

        elif self.getCurrentToken().type == "PRINT":
            self.current += 1
            if self.getCurrentToken().type == "POPEN":
                line = self.getCurrentToken().line
                self.current += 1
                while self.getCurrentToken().type != "PCLOSE":
                    if self.getCurrentToken().line != line or self.getCurrentToken().type in cant:
                        raise Exception(
                            'Syntatic error (expecting paranteses after PRINT statements) in line {}'.formar(self.getCurrentToken().line))
                    elif self.getCurrentToken().type in parameters:
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
                    raise Exception(
                        'Syntatic error (expecting ; after PRINT call) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception(
                    'Syntatic error (expecting ( after PRINT) in line {}'.format(self.getCurrentToken().line))

        elif self.getCurrentToken().type == "RETURN":
            self.current += 1
            parameters = ["INTEGER", "BOOLEAN", "LETTER", "NUM"]
            if self.getCurrentToken().type in parameters:
                if self.getCurrentToken().type == "LETTER":
                    if self.getCurrentToken().lexeme.islower() == False:
                        raise Exception('Syntatic error (invalid argument for RETURN) in line {}'.format(self.getCurrentToken().line))
                    else:
                        self.current += 1
                        if self.getCurrentToken().type == "SEMICOLON":
                            self.current += 1
                            self.flag = 0
                            return
                        else:
                            raise Exception(
                                'Syntatic error (expecting ; but recieved invalid argument) in line {}'.format(self.getCurrentToken().line))
                else:
                    self.current += 1
                    if self.getCurrentToken().type == "SEMICOLON":
                        self.current += 1
                        self.flag = 0
                        return
                    else:
                        raise Exception('Syntatic error (expecting ; but recieved invalid argument) in line {}'.format(self.getCurrentToken().line))
            else:
                raise Exception(
                    'Syntatic error (invalid type as return) in line {}'.format(self.getCurrentToken().line))
        else:
            raise Exception(
                'Syntatic error (unexpect argument of system call) in line {}'.format(self.getCurrentToken().line))
