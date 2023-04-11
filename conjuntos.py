def conjunto_primero_token(token, tokens_recursivos, tokens_terminales, tokens_no_terminales, producciones):
    primero = set()

    if token in tokens_terminales:
        primero.add(token)
        return primero

    if token in tokens_no_terminales and None in producciones[token]:
        primero.add(None)

    for produccion in producciones[token]:
        conjuntos_primero = []
        conjunto_interseccion = tokens_terminales | tokens_no_terminales | {None}
        if produccion is not None:
            for token_prod in produccion:
                if token_prod not in tokens_recursivos:
                    primero_token = conjunto_primero_token(token_prod, tokens_recursivos | set(token_prod), tokens_terminales, tokens_no_terminales, producciones)
                    conjuntos_primero.append(primero_token)
                    conjunto_interseccion &= primero_token

            if None in conjunto_interseccion:
                primero.add(None)

            for conjunto in conjuntos_primero:
                primero |= conjunto.difference({None})
                if None not in conjunto:
                    break

    return primero


def conjunto_primero(tokens_terminales, tokens_no_terminales, producciones):
    conjunto_primero = dict()
    for token in tokens_terminales | tokens_no_terminales:
        conjunto_primero[token] = conjunto_primero_token(token, set(token), tokens_terminales, tokens_no_terminales, producciones)
        #print("PRI(", token, "): ", conjunto_primero_token(token, set(token), tokens_terminales, tokens_no_terminales, producciones))
    return conjunto_primero

def conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente = dict()
    siguiente[token_inicial] = {""}

    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            if produccion is not None:
                for index, token_prod in enumerate(produccion):
                    conjunto_primero_beta = set()
                    conjunto_primero_beta_interseccion =  tokens_terminales | tokens_no_terminales | {None}

                    if token_prod in tokens_no_terminales: # A -> a B b
                        for t in produccion[index+1:]:
                            conjunto_primero = conjunto_primero_token(t, tokens_terminales, tokens_no_terminales, producciones)
                            conjunto_primero_beta |= conjunto_primero
                            conjunto_primero_beta_interseccion &= conjunto_primero

                        if token_prod in siguiente:
                            siguiente[token_prod] |= conjunto_primero_beta.difference({None})
                        else:
                            siguiente[token_prod] = conjunto_primero_beta.difference({None})

                        if index == len(produccion) or None in conjunto_primero_beta_interseccion:  # A -> a B  or A -> a B b con eps in PRI(b)
                            if token_prod in siguiente:
                                siguiente[token_prod] |= siguiente[token]
                            else:
                                siguiente[token_prod] = siguiente[token]

    print("conjunto siguiente:", siguiente)
    return siguiente

def construccion_tabla(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente = conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    tabla = dict()

    for token_no_terminal in tokens_no_terminales:
        for token_terminal in tokens_terminales|{""}:
            tabla[token_no_terminal, token_terminal] = []
            print()

    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            if produccion is not None:
                primero = set()
                for t in produccion:
                    primero |= conjunto_primero_token(t, tokens_terminales, tokens_no_terminales, producciones)

                for elemento in primero&tokens_terminales:
                    tabla[token, elemento] = produccion # que añado ?

                if None in primero:
                    for b in tokens_terminales&siguiente[token]:
                        tabla[token, b] = produccion  # que añado ?
                    if "" in siguiente[token]:
                        tabla[token, ""] = produccion  # que añado ?
                        print()

    for token_no_terminal in tokens_no_terminales:
        for token_terminal in tokens_terminales|{""}:
            if tabla[token_no_terminal, token_terminal] == dict():
                tabla[token_no_terminal, token_terminal] = "error" # que añado ?
                #error

    print(tabla)
    return tabla