import sys
from lexer_files.Scanner import Scanner
from parser_files.Parser import Parser

if __name__ == "__main__":
    #Abrir arquivo de entrada
    try:
        archive = open("program.txt", "r")
        program = "".join(archive.readlines())
        archive.close()
    except Exception:
        sys.exit(1)
    #Fazendo a análise léxica da entrada
    lexer = Scanner(program)
    tableTokens = lexer.scan()

    for i in tableTokens:
        print(i)

    #Fazendo a análise sintática da entrada
    parser = Parser(tableTokens)
    parser.start()
