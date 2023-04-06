def conjunto_primero_token(token, tokens_terminales, tokens_no_terminales, producciones):
    primero_viejo = set()
    primero = set()
    primera_iter = True

    if token in tokens_terminales:
        primero.add(token)
        return primero

    if token in tokens_no_terminales and None in producciones[token]:
        primero.add(None)

    while primero_viejo != primero or primera_iter:
        primera_iter = False
        primero_viejo = primero.copy()

        for produccion in producciones[token]:
            conjuntos_primero = []
            conjunto_interseccion = tokens_terminales | tokens_no_terminales
            conjunto_interseccion |= {None}
            if produccion is not None:
                for token_prod in produccion:
                    if token_prod != token:
                        primero_token = conjunto_primero_token(token_prod, tokens_terminales, tokens_no_terminales, producciones)
                        #print("Aux Pri(", token_prod, "):", primero_token)
                        conjuntos_primero.append(primero_token)
                        #print("conjuntos primero:", conjuntos_primero)
                        conjunto_interseccion &= primero_token
                elementos_conjuntos_primero = set().union(*conjuntos_primero)
                #print("elementos conjunto primero:", elementos_conjuntos_primero)
                #print("conjunto primero interseccion:", conjunto_interseccion)
                #print("conjuntos_primero", conjuntos_primero)

                if None in conjunto_interseccion:
                    primero.add(None)
                if len(conjuntos_primero) == 1:
                    primero |= conjuntos_primero[0]
                else:

                    for i, conjunto_1 in enumerate(conjuntos_primero):
                        #print("i:", i, "conjunto_1:", conjunto_1)
                        #print("HOLAAA", conjuntos_primero[:1])
                        for elemento in conjunto_1:
                            #print("elemento: ", elemento)
                            #print("conjuntos_primero[:i - 1]:", conjuntos_primero[:i-1])
                            conjunto_interseccion = tokens_terminales | tokens_no_terminales | {None}
                            for j in range(0, i):
                                #print("conjunto ", j, ": ", conjuntos_primero[j])
                                conjunto_interseccion &= conjuntos_primero[j]
                            #print("interseccion i-1 conjutnos primero:", conjunto_interseccion, ", i-1:", i-1)
                            if elemento is not None and i == 0:
                                primero.add(elemento)
                                #print("primero tras añadir ", elemento, ":", primero)
                            elif elemento is not None and None in conjunto_interseccion:
                                primero.add(elemento)
                                #print("primero tras añadir ", elemento, ":", primero)


    return primero


def conjunto_primero(tokens_terminales, tokens_no_terminales, producciones):
    conj = tokens_terminales | tokens_no_terminales
    for token in conj:
        print("\t\t Pri(", token ,"):", conjunto_primero_token(token, tokens_terminales, tokens_no_terminales, producciones))


def conjunto_siguiente(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    siguiente_viejo = dict()
    siguiente = dict()

    siguiente[token_inicial] = "$" # todo cambiar

    while siguiente != siguiente_viejo:
        siguiente_viejo = siguiente

        for token in tokens_no_terminales:
            for produccion in producciones[token]:
                for index, token_prod in enumerate(produccion):
                    conjunto_primero_beta = set()

                    if token_prod in tokens_no_terminales: # A -> a B b
                        for t in produccion[index+1:]:
                            conjunto_primero_beta.add(conjunto_primero(t, tokens_terminales, tokens_no_terminales, producciones))
                        siguiente[token_prod] = conjunto_primero_beta
                    if index == len(produccion) or None in conjunto_primero_beta:  # A -> a B  or A -> a B b con eps in PRI(b)
                        siguiente[token_prod].add(siguiente[token])
    return siguiente