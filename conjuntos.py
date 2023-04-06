def conjunto_primero_token(token, tokens_terminales, tokens_no_terminales, producciones):
    primero = set()

    if token in tokens_terminales:
        primero.add(token)
        return primero

    if token in tokens_no_terminales and None in producciones[token]:
        primero.add(None)

    for produccion in producciones[token]:
        conjuntos_primero = []
        conjunto_interseccion = tokens_terminales | tokens_no_terminales
        conjunto_interseccion |= {None}
        if produccion is not None:
            for token_prod in produccion:
                if token_prod != token:
                    primero_token = conjunto_primero_token(token_prod, tokens_terminales, tokens_no_terminales, producciones)
                    conjuntos_primero.append(primero_token)
                    conjunto_interseccion &= primero_token

            if None in conjunto_interseccion:
                primero.add(None)
            if len(conjuntos_primero) == 1:
                primero |= conjuntos_primero[0]
            else:

                for i, conjunto_1 in enumerate(conjuntos_primero):
                    for elemento in conjunto_1:
                        conjunto_interseccion = tokens_terminales | tokens_no_terminales | {None}
                        for j in range(0, i):
                            conjunto_interseccion &= conjuntos_primero[j]
                        if elemento is not None and i == 0:
                            primero.add(elemento)
                        elif elemento is not None and None in conjunto_interseccion:
                            primero.add(elemento)

    return primero


def conjunto_primero(tokens_terminales, tokens_no_terminales, producciones):
    conjunto_primero = dict()
    for token in tokens_terminales | tokens_no_terminales:
        print("\t\t Pri(", token ,"):", conjunto_primero_token(token, tokens_terminales, tokens_no_terminales, producciones))
        conjunto_primero[token] = conjunto_primero_token(token, tokens_terminales, tokens_no_terminales, producciones)

    return conjunto_primero

def conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente = dict()
    siguiente[token_inicial] = {""} # TODO ?

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
                        print("conjunto_primero_beta: ", conjunto_primero_beta)

                        if token_prod in siguiente:
                            print("añado a siguiente[", token_prod, "]:", conjunto_primero_beta.difference({None}))
                            siguiente[token_prod] |= conjunto_primero_beta.difference({None})
                        else:
                            print("siguiente[", token_prod, "]:", conjunto_primero_beta.difference({None}))
                            siguiente[token_prod] = conjunto_primero_beta.difference({None})

                        if index == len(produccion) or None in conjunto_primero_beta_interseccion:  # A -> a B  or A -> a B b con eps in PRI(b)
                            print("añado a siguiente[", token_prod, "] siguiente[", token, "]", siguiente[token])
                            siguiente[token_prod] |= siguiente[token]

    print("conjunto siguiente:", siguiente)
    return siguiente