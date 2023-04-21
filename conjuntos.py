import LL1
def conjunto_primero_token(token, tokens_recursivos, tokens_terminales, tokens_no_terminales, producciones):
    primero = set()

    if token in tokens_terminales:
        primero.add(token)
        return primero

    if token in tokens_no_terminales and None in producciones[token]:
        primero.add(None)

    for produccion in producciones[token]:
        if produccion is not None:
            epsilon = True
            for token_prod in produccion:
                if token_prod not in tokens_recursivos:
                    primero_token = conjunto_primero_token(token_prod, tokens_recursivos | set(token_prod), tokens_terminales, tokens_no_terminales, producciones)
                    primero |= primero_token.difference({None})
                    if None not in primero_token:
                        epsilon = False
                        break
            if epsilon:
                primero |= {None}

    return primero


def conjunto_primero(tokens_terminales, tokens_no_terminales, producciones):
    conjunto_primero = dict()
    for token in tokens_terminales | tokens_no_terminales:
        conjunto_primero[token] = conjunto_primero_token(token, set(token), tokens_terminales, tokens_no_terminales, producciones)
        print("PRI(", token, "): ", conjunto_primero_token(token, set(token), tokens_terminales, tokens_no_terminales, producciones))
    return conjunto_primero

def conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente_viejo = dict()
    siguiente = dict()
    siguiente[token_inicial] = {"$"}
    while siguiente != siguiente_viejo:
        siguiente_viejo = siguiente.copy()
        for token in tokens_no_terminales:
            for produccion in producciones[token]:
                if produccion is not None:
                    for index, token_prod in enumerate(produccion):
                        conjunto_primero_beta = set()
                        if token_prod in tokens_no_terminales: # A -> a B b
                            epsilon = True
                            # Calculate Pri(þ)
                            for t in produccion[index+1:]:
                                conjunto_primero_t = conjunto_primero_token(t, set(t), tokens_terminales, tokens_no_terminales, producciones)
                                conjunto_primero_beta |= conjunto_primero_t.difference({None})
                                if None not in conjunto_primero_t:
                                    epsilon = False
                                    break

                            if epsilon:
                                conjunto_primero_beta |= {None}

                            if token_prod in siguiente:
                                siguiente[token_prod] |= conjunto_primero_beta.difference({None})
                            else:
                                siguiente[token_prod] = conjunto_primero_beta.difference({None})

                            if index == len(produccion) or None in conjunto_primero_beta:  # A -> a B  or A -> a B b con eps in PRI(b)
                                if token_prod in siguiente and token in siguiente:
                                    siguiente[token_prod] |= siguiente[token]
                                elif token in siguiente:
                                    siguiente[token_prod] = siguiente[token]

    return siguiente


def construccion_tabla(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente = conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    tabla = dict()

    for token_no_terminal in tokens_no_terminales:
        for token_terminal in tokens_terminales | {"$"}:
            tabla[token_no_terminal, token_terminal] = []

    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            primero = set()
            if produccion is not None:
                epsilon = True
                for t in produccion:
                    conj_pri = conjunto_primero_token(t, set(t), tokens_terminales, tokens_no_terminales, producciones)
                    primero |= conj_pri.difference({None})
                    if None not in conj_pri:
                        epsilon = False
                        break

                if epsilon:
                    primero |= {None}
            else:
                primero = {None}

            for elemento in primero & tokens_terminales:
                tabla[token, elemento].append(produccion)

            if None in primero:
                for b in tokens_terminales & siguiente[token]:
                    tabla[token, b].append(produccion)
                if "$" in siguiente[token]:
                    tabla[token, "$"].append(produccion)

    for token_no_terminal in tokens_no_terminales:
        for token_terminal in tokens_terminales | {"$"}:
            if tabla[token_no_terminal, token_terminal] == dict():
                tabla[token_no_terminal, token_terminal] = "error"  # que añado ?
                # error
    print(tabla)

    tabla = LL1.simulate(tabla, token_inicial, tokens_terminales, "'(' 'x' ';' '(' 'x' ')' ')' $")
    return tabla
