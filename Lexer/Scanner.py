from Lexer.Token import Token


class Scanner:
    def __init__(self, program):
        self. tokens = []
        self.current = 0
        self.start = 0
        self.line = 1
        self.program = program

    def nextChar(self):
        self.current += 1
        return self.program[self.current - 1]

    def scan(self):
        self.scanTokens()
        self.tokens.append(Token('END', '', self.line))
        return self.tokens

    def scanTokens(self):
        while self.current != len(self.program):
            self.start = self.current
            char = self.nextChar()

            if char == ' ' or char == '\t' or char == '\r':
                pass
            elif char == '\n':
                self.line += 1
            # verifica os tokens "(",")","{","}"
            elif char == '(' or char == ')' or char == '{' or char == '}':
                self.tokens.append(self.scanDelimiterToken(char))
            # verifica os tokens "+", "-", "*", "/"
            elif char == '+' or char == '-' or char == '*' or char == '/':
                self.tokens.append(self.scanArithmeticToken(char))
            # verifica os tokens "=", ==", "!=", "<", "<=", ">", ">="
            elif char == '=' or char == '==' or char == '!=' or char == '<' or char == '<=' or char == '>' or char == '>=':
                self.tokens.append(self.scanBooleanToken(char))
            # veerifica os tokens "," e ";"
            elif char == ',' or char == ';':
                self.tokens.append(self.scanSeparatorToken(char))
            # verifica os tokens numéricos
            elif char.isnumeric():
                self.tokens.append(self.scanNumericToken())
            # verifica os tokens de letras, identificadores ou palavras reservadas
            elif char.isalpha():
                self.tokens.append(self.scanLetterToken())
            # verifica se ouve um erro
            else:
                print('Error in line {}'.format(self.line))
                exit(2)

    def scanDelimiterToken(self, char):
        if char == '(':
            return Token('POPEN', self.program[self.start:self.current], self.line)
        elif char == ')':
            return Token('PCLOSE', self.program[self.start:self.current], self.line)
        elif char == '{':
            return Token('BOPEN', self.program[self.start:self.current], self.line)
        elif char == '}':
            return Token('BCLOSE', self.program[self.start:self.current], self.line)

    def scanArithmeticToken(self, char):
        if char == '+':
            return Token('ADD', self.program[self.start:self.current], self.line)
        elif char == '-':
            return Token('SUB', self.program[self.start:self.current], self.line)
        elif char == '*':
            return Token('MUL', self.program[self.start:self.current], self.line)
        elif char == '/':
            return Token('DIV', self.program[self.start:self.current], self.line)

    def scanBooleanToken(self, char):
        if char == '=':
            if self.lookAhead() == '=':
                return Token('EQUAL', self.program[self.start:self.current], self.line)
            else:
                return Token('ATTR', self.program[self.start:self.current], self.line)
        elif char == '!' and self.lookAhead() == '=':
            return Token('DIFF', self.program[self.start:self.current], self.line)
        elif char == '<':
            if self.lookAhead() == '=':
                return Token('LESSEQUAL', self.program[self.start:self.current], self.line)
            else:
                return Token('LESS', self.program[self.start:self.current], self.line)
        elif char == '>':
            if self.lookAhead() == '=':
                return Token('GREATEREQUAL', self.program[self.start:self.current], self.line)
            else:
                return Token('GREATER', self.program[self.start:self.current], self.line)

    def scanSeparatorToken(self, char):
        if char == ',':
            return Token('COMMA', self.program[self.start:self.current], self.line)
        else:
            return Token('SEMICOLON', self.program[self.start:self.current], self.line)

    def scanNumericToken(self):
        while self.lookAhead().isnumeric():
            self.nextChar()
        return Token('NUM', self.program[self.start:self.current], self.line)

    def scanLetterToken(self):
        while self.lookAhead().isalpha():
            self.nextChar()
        return Token('LETTER', self.program[self.start:self.current], self.line)

    def lookAhead(self):
        if self.current != len(self.program):
            return self.program[self.current]
        else:
            return '\0'