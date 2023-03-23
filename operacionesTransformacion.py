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
    nuevos_tokens_no_terminales, nuevas_producciones = eliminacion_simolos_no_termibales(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    print("soy una gramatica no vacia?", token_inicial in nuevas_producciones)
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

def eliminacion_no_accesibles(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = [token_inicial]
    nuevo = [token_inicial]


    for produccion in producciones[token_inicial]:
        if produccion is not None:
            for token in produccion:
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
    print("tokens nullable", nullable_tokens)
    print(tokens_no_terminales)
    for token in tokens_no_terminales:
        print("token", token)
        if None in producciones[token]:
            # quitamos la produccion epsilon
            producciones[token].remove(None)

        for produccion in producciones[token]:
            nullable_tokens_produccion = set(produccion) & nullable_tokens
            #print("nullable_tokens_produccion", nullable_tokens_produccion)
            indices_token_nullable = {produccion.index(null_token) for null_token in nullable_tokens_produccion}
            #print("indices_token_nullable", indices_token_nullable)
            # todo si len(nullable_tokens_produccion) == len(produccion) a
            combinaciones = []
            for i in range(1, len(indices_token_nullable) + 1):     # creamos todas las combinaciones posibles
                combinaciones.extend(list(x) for x in itertools.combinations(indices_token_nullable, i))
            print("combinaciones", combinaciones)

            for lista in combinaciones:
                nueva_produccion = [x for i, x in enumerate(produccion) if i not in lista]
                print("nueva_produccion", nueva_produccion)
                if ((nueva_produccion != [] and token != token_inicial) or (nueva_produccion == [] and token == token_inicial)) \
                        and nueva_produccion not in producciones[token]:
                    producciones[token].append(nueva_produccion)

    print("fin")
    return producciones

def tokens_unitarios_alanzables(token, tokens_terminales, tokens_no_terminales, producciones):
    print("TOKEN", token)
    print()
    print()
    viejo = set()
    nuevo = set()
    print(producciones[token])
    for produccion in producciones[token]:
        print(produccion)
        if len(produccion) == 1 and produccion[0] in tokens_no_terminales:
            print("elimino:", produccion, "y lo añado a nuevo")
            producciones[token].remove(produccion)
            nuevo.add(produccion[0])

    if nuevo == viejo:
        print("fin")
        return producciones

    print("nuevo:", nuevo)
    while viejo != nuevo:
        print("nueva iteracion")
        print("viejo:", viejo)
        print("nuevo:", nuevo)

        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo.copy()

        for token1 in nuevos_token:
            print("par: (", token1, ",", token1, ")")
            aniadido = False
            for produccion in producciones[token1]:
                print("produccion", produccion)
                if len(produccion) == 1 and produccion[0] in tokens_no_terminales:
                    print("nuevo antes de aniadir", nuevo)
                    nuevo.add(produccion[0])
                    print("nuevo despues de aniadir", nuevo)
                    print("viejo:", viejo)
                    print("par: (", token1, ",", produccion[0], ")")
                elif not aniadido:
                    aniadido = True
                    print("producciones[token1]", producciones[token1])
                    for produccion_aniadir in producciones[token1]:
                        print("posible prodccion a añadir", produccion_aniadir)
                        print("producciones[token] antes", producciones[token])
                        if (len(produccion_aniadir) > 1 or (len(produccion_aniadir) == 1 and produccion_aniadir[0] in tokens_terminales)) and produccion_aniadir not in producciones[token]:
                            producciones[token].append(produccion_aniadir)
                            print("producciones[token] despues", producciones[token])
            print("viejo:", viejo)
            print("nuevo:", nuevo)
    print("fin")
    return producciones


def eliminacion_producciones_unitarias(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    tokens_unitarios = dict()
    lista_unit_pairs = set()
    for token in tokens_no_terminales:
        print("øøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøøø", token)
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

