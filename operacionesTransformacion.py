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

def gramatica_no_vacia(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    _, nuevas_producciones = eliminacion_simolos_no_termibales(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    print(token_inicial in nuevas_producciones)
    return token_inicial in nuevas_producciones

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


def is_nullable(token, tokens_no_terminales, producciones):
    if None in producciones[token]:
        return True

    viejo = set()
    nuevo = set(token for produccion in producciones[token] if produccion is not None for token in produccion) | set(token)

    while viejo != nuevo:
        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo

        for token1 in nuevos_token:
            if None in producciones[token1]:
                return True
            if token1 in tokens_no_terminales:
                nuevo |= set(token1 for produccion in producciones[token1] for token1 in produccion)

    return False

def eliminacion_producciones_epsilon(token_inicial, tokens_no_terminales, producciones):
    nullable_tokens = {token for token in tokens_no_terminales if is_nullable(token, tokens_no_terminales, producciones)}

    for token in tokens_no_terminales:
        if token in nullable_tokens:
            producciones[token].remove(None) # quitamos la produccion epsilon

        for produccion in producciones[token]:
            nullable_tokens_produccion = set(produccion) & nullable_tokens
            indices_token_nullable = {produccion.index(null_token) for null_token in nullable_tokens_produccion}
            combinaciones = []
            for i in range(1, len(indices_token_nullable) + 1):     # creamos todas las combinaciones posibles
                combinaciones.extend(list(x) for x in itertools.combinations(indices_token_nullable, i))

            for lista in combinaciones:
                nueva_produccion = [x for i, x in enumerate(produccion) if i not in lista]
                if (nueva_produccion != [] or (nueva_produccion == [] and token == token_inicial)) \
                        and nueva_produccion not in producciones[token]:
                    producciones[token].append(nueva_produccion)

    return producciones

def tokens_unitarios_alanzables(token, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set()
    nuevo = set()
    for produccion in producciones[token]:
        if len(produccion) == 1 and produccion[0] in tokens_no_terminales:
            producciones[token].remove(produccion)
            nuevo.add(produccion[0])

    while viejo != nuevo:
        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo.copy()

        for token1 in nuevos_token:
            aniadido = False
            for produccion in producciones[token1]:
                if produccion is not None and len(produccion) == 1 and produccion[0] in tokens_no_terminales: # produccion unitaria encontrada
                    nuevo.add(produccion[0])
                elif not aniadido:
                    aniadido = True
                    for produccion_aniadir in producciones[token1]:
                        if (len(produccion_aniadir) > 1 or (len(produccion_aniadir) == 1 and produccion_aniadir[0] in tokens_terminales)) and produccion_aniadir not in producciones[token]:
                            producciones[token].append(produccion_aniadir)

    return producciones


def eliminacion_producciones_unitarias(token_inicial, tokens_terminales, tokens_no_terminales, producciones):

    for token in tokens_no_terminales:
        producciones = tokens_unitarios_alanzables(token, tokens_terminales, tokens_no_terminales, producciones)

    return producciones

def forma_normal_chomsky(token_inicial, tokens_terminales, tokens_no_terminales, producciones):

    return token_inicial, tokens_terminales, tokens_no_terminales, producciones


def eliminacion_producciones_epsilon_vieja(token_inicial, tokens_terminales, tokens_no_terminales, producciones):

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

