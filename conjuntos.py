def conjunto_primero(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    primero = dict()
    for x in tokens_terminales.union(tokens_no_terminales):
        conunto = set()

        primero[x] = conunto
    return primero

def conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente = dict()
    for x in tokens_no_terminales:
        conunto = set()

        siguiente[x] = conunto
    return siguiente