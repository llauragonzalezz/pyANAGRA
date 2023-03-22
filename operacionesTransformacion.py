import itertools


def eliminacion_simbolos_inutiles(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set()
    nuevo = set(token for produccion in producciones[token_inicial] if produccion is not None for token in produccion) \
            | set(token_inicial)

    while viejo != nuevo:
        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo

        for token in nuevos_token:
            if token in tokens_no_terminales:
                nuevo |= set(token for produccion in producciones[token] if produccion is not None for token in produccion)

    tokens_terminales &= set(token for token in nuevo if token in tokens_terminales)
    tokens_a_eliminar = tokens_no_terminales.difference(set(token for token in nuevo if token in tokens_no_terminales))
    producciones = {clave: valor for clave, valor in producciones.items() if clave not in tokens_a_eliminar}

    return tokens_terminales, tokens_no_terminales, producciones


def eliminacion_simolos_no_termibales(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set(token_inicial)
    nuevo = set()

    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            if produccion is None or set(produccion) <= tokens_terminales:
                nuevo |= set(token)

    while viejo != nuevo:
        viejo = nuevo
        for token in tokens_no_terminales:
            for produccion in producciones[token]:
                if produccion is None or set(produccion) <= tokens_terminales | viejo:
                    nuevo |= set(token)

    nuevas_producciones = dict()
    for token in nuevo:
        lista_producciones = []
        for produccion in producciones[token]:
            print(produccion)
            if produccion is None or set(produccion) <= nuevo | tokens_terminales:
                lista_producciones.append(produccion)

        nuevas_producciones[token] = lista_producciones

    return nuevo, nuevas_producciones

def eliminacion_no_accesibles(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = [token_inicial]
    nuevo = [token_inicial]

    for producciones in producciones[token_inicial]:
        if producciones is not None:
            for token in producciones:
                if (token in tokens_no_terminales or token in tokens_terminales) and token not in nuevo:
                    nuevo.append(token)

    while viejo != nuevo:
        viejo = nuevo
        nuevo = viejo
        # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
        # por terminales o elementos en viejo
        for tokenViejo in viejo:
            if tokenViejo in tokens_no_terminales:
                for producciones in producciones[tokenViejo]:
                    if producciones is not None:
                        for token in producciones:
                            if (token in tokens_no_terminales or token in tokens_terminales) and token not in nuevo:
                                nuevo.append(token)

    tokens_no_terminales = [value for value in nuevo if value in tokens_no_terminales]
    tokens_terminales = [value for value in nuevo if value in tokens_terminales]

    # producciones se acutualiza a aquellas que esten compuestas por tokenes pertenecientes a nuevo o a terminales
    tokens_terminales = nuevo
    nuevas_reglas = dict()
    for nuevo_no_terminal in nuevo:
        nuevas_producciones = []
        for produccion in producciones[nuevo_no_terminal]:
            todo_terminales_o_nuevo = True
            if produccion is not None:
                for token in produccion:
                    if (token not in tokens_terminales) or (token not in nuevo):
                        todo_terminales_o_nuevo = False
                        break
            if todo_terminales_o_nuevo:
                nuevas_producciones.append(produccion)
        nuevas_reglas[nuevo_no_terminal] = nuevas_producciones

    producciones = nuevas_reglas
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

def factorizacion_a_izquierda(token_inicial, tokens_terminales, tokens_no_terminales, producciones):

    for token in tokens_no_terminales:
        # si el token tiene mas de una posible produccion y no tiene producciones epsilon
        print(token)
        print("len(producciones[token]) > 1", len(producciones[token]) > 1)
        print("None not in producciones[token]", None not in producciones[token])
        if len(producciones[token]) > 1 and None not in producciones[token]:
            print(producciones[token])
            indiceCoincidencia = 0
            diferentes = False
            for indice in range(len(producciones[token][0])):
                print("indice", indice)
                for produccion in producciones[token]:
                    if len(produccion) - 1 < indice or produccion[indice] != producciones[token][0][indice]:
                        print("STOP")
                        diferentes = True
                        break
                if diferentes:
                    break
                indiceCoincidencia += 1
            print("indice de coincidencia = ", indiceCoincidencia)
            # transformamos la gramatica factorizando los elementos comunes
            if diferentes and indiceCoincidencia > 0:
                print("entro")
                nombre = "fact_" + token
                print( [produccion[indiceCoincidencia+1:] for produccion in producciones[token] if produccion[indiceCoincidencia+1:]])
                producciones[nombre] = [produccion[indiceCoincidencia+1:] for produccion in producciones[token] if produccion[indiceCoincidencia+1:]]
                tokens_no_terminales.add(nombre)
                producciones[token] = producciones[token][0][:indiceCoincidencia].append(nombre)
                break
        print(producciones)
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones


def eliminar_recursividad_izquierda(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    for i in range(len(tokens_no_terminales)):
        for j in range(i-1):
            for produccion in producciones[tokens_no_terminales[i]]:
                if produccion[0] is not None and produccion[0] == tokens_no_terminales[j]:
                    producciones[tokens_no_terminales[i]].append(lista + produccion for lista in producciones[tokens_no_terminales[j]])

    return token_inicial, tokens_terminales, tokens_no_terminales, producciones
    

def eliminacion_producciones_epsilon(token_inicial, tokens_terminales, tokens_no_terminales, producciones):

    for token in tokens_no_terminales:
        print(token)
        if None in producciones[token]:
            # quitamos la produccion epsilon
            producciones[token].remove(None)

            # por cada produccion que contuviese el token la añadimos una en donde no este
            for token_1 in tokens_no_terminales:
                for produccion in producciones[token_1]:
                    if produccion is not None and token in produccion:
                        indices = [i for i, x in enumerate(produccion) if x == token]
                        print("indices", indices)
                        combinaciones = []
                        for i in range(1, len(indices)+1):
                            combinaciones.extend(list(x) for x in itertools.combinations(indices, i))
                        print("posibles combinaciones: ", combinaciones)
                        for lista in combinaciones:
                            nueva_produccion = [x for i, x in enumerate(produccion) if i not in lista]
                            if nueva_produccion not in producciones[token_1]:
                                producciones[token_1].append(nueva_produccion)
                        print(producciones[token_1])

    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

def eliminacion_ciclos(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

