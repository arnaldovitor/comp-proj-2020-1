#classe token, e seus atributos tipo, lexema (palavra em si) e a linha onde se encontra
class Token:
    def __init__(self, type, lexeme, line):
        self.type = type
        self.lexeme = lexeme
        self.line = line

    def __str__(self):
        return "Type:{} Lexeme:{} Line:{}".format(self.type, self.lexeme, self.line)
