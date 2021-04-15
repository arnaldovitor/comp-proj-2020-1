import sys
from Lexer.Scanner import Scanner

if __name__ == "__main__":
    try:
        archive = open("program.txt", "r")
        program = "".join(archive.readlines())
        archive.close()
    except Exception:
        sys.exit(1)
    lexer = Scanner(program)
    tableTokens = lexer.scan()

    for i in tableTokens:
        print(i)
