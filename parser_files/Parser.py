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
        self.statement_list()
        return

    def statement_list(self):
        if self.getCurrentToken().type == "END":
            return
        else:
            self.statement()
            self.statement_list()
            return

    def statement(self):
        if self.getCurrentToken().type == "INTEGER" or self.getCurrentToken().type == "BOOLEAN":
            self.var_statement()
            return

    # análise sintática para cadeia de tokens que começam com INTEGER ou BOOLEAN
    def var_statement(self):
        self.current += 1
        if self.getCurrentToken().type == "LETTER" and self.getCurrentToken().lexeme.islower():
            self.current += 1
            if self.getCurrentToken().type == "ATTR":
                self.current += 1
                self.checkExpression()
                if self.getCurrentToken().type == "SEMICOLON":
                    self.current+=1
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





