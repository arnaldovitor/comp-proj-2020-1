import sys
import os.path
from lexer_files.Scanner import Scanner
from parser_files.Parser import Parser
from parser_files.Semantic import Semantic
from parser_files.Conversor import Conversor

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

    SymbolsTable = parser.symbols
    print()
    for i in range(len(SymbolsTable)):
        print(SymbolsTable[i])

    SymbolsSemantic = parser.symbolsSemantic
    
    semantic = Semantic(SymbolsSemantic)
    semantic.start()

    print()
    conversor = Conversor(SymbolsSemantic)
    conversor.start()

    documento = open("saida.txt","a")
    documento.write(conversor.string)
    documento.close()
