def hasLogicSymbol(tokenLookAhead):
    return tokenLookAhead.type == "EQUAL" or tokenLookAhead.type == "DIFF" or tokenLookAhead.type == "LESS" or tokenLookAhead.type == "LESSEQUAL" or tokenLookAhead.type == "GREATER" or tokenLookAhead.type == "GREATEREQUAL"

def hasArithmeticSymbol(tokenLookAhead):
    return tokenLookAhead.type == "ADD" or tokenLookAhead.type == "SUB" or tokenLookAhead.type == "DIV" or tokenLookAhead.type == "MUL"