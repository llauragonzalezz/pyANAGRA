
def eliminacion_no_terminales_optimizada(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set()
    nuevo = set()

    # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
    # por terminales
    for noTerminal in tokens_no_terminales:
        todo_no_terminales = True
        for produccion in producciones[noTerminal]:
            if produccion is not None:
                for token in produccion:
                    if tokens_terminales.isdisjoint(set(token)):
                        todo_no_terminales = False
                        break
                if not todo_no_terminales:
                    break

        if todo_no_terminales:
            nuevo.add(noTerminal)

    while viejo != nuevo:
        viejo = nuevo
        nuevo = viejo
        # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
        # por terminales o elementos en viejo
        for noTerminal in tokens_no_terminales:
            todo_no_terminales_o_viejo = True
            for produccion in producciones[noTerminal]:
                if produccion is not None:
                    for token in produccion:
                        if tokens_terminales.isdisjoint(set(token)) or viejo.isdisjoint(set(token)):
                            todo_no_terminales_o_viejo = False
                            break
                    if not todo_no_terminales_o_viejo:
                        break

            if todo_no_terminales_o_viejo:
                nuevo.add(noTerminal)

    # producciones se acutualiza a aquellas que esten compuestas por tokenes pertenecientes a nuevo o a terminales
    tokens_terminales = nuevo
    nuevas_reglas = dict()
    for nuevo_no_terminal in nuevo:
        nuevas_producciones = []
        for produccion in producciones[nuevo_no_terminal]:
            todo_terminales_o_nuevo = True
            if produccion is not None:
                for token in produccion:
                    if tokens_terminales.isdisjoint(set(token)) or nuevo.isdisjoint(set(token)):
                        todo_terminales_o_nuevo = False
                        break
            if todo_terminales_o_nuevo:
                nuevas_producciones.append(produccion)
        nuevas_reglas[nuevo_no_terminal] = nuevas_producciones

    producciones = nuevas_reglas
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

def eliminacion_no_terminales(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = []
    nuevo = []

    # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
    # por terminales
    for noTerminal in tokens_no_terminales:
        todo_no_terminales = True
        for produccion in producciones[noTerminal]:
            if produccion is not None:
                for token in produccion:
                    if token not in tokens_terminales:
                        todo_no_terminales = False
                        break
                if not todo_no_terminales:
                    break

        if todo_no_terminales:
            nuevo.append(noTerminal)

    while viejo != nuevo:
        viejo = nuevo
        nuevo = viejo
        # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
        # por terminales o elementos en viejo
        for noTerminal in tokens_no_terminales:
            todo_no_terminales_o_viejo = True
            for produccion in producciones[noTerminal]:
                if produccion is not None:
                    for token in produccion:
                        if (token not in tokens_terminales) or (token not in viejo):
                            todo_no_terminales_o_viejo = False
                            break
                    if not todo_no_terminales_o_viejo:
                        break

            if todo_no_terminales_o_viejo and noTerminal not in nuevo:
                nuevo.append(noTerminal)

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

def eliminacion_no_accesibles(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = [token_inicial]
    nuevo = [token_inicial]

    for producciones  in producciones[token_inicial]:
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
        if len(producciones[token]) > 1 and None not in producciones[token]:
            indiceCoincidencia = 0
            diferentes = False
            for indice in range(len(producciones[token][0])):
                for produccion in producciones[token]:
                    if len(produccion) < indice or produccion[indice] != producciones[token][0][indice]:
                        diferentes = True
                        break
                indiceCoincidencia += 1

            # transformamos la gramatica factorizando los elementos comunes
            if diferentes and indiceCoincidencia > 0:
                nombre = "fact_" + token
                producciones[nombre] = [produccion[indiceCoincidencia+1:] for produccion in producciones[token] if produccion[indiceCoincidencia+1:]]
                tokens_no_terminales.add(nombre)
                producciones[token] = producciones[token][0][:indiceCoincidencia]
                break

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
        if None in producciones[token]:
            # quitamos la produccion epsilon
            producciones[token].remove(None)

            # por cada produccion que contuviese el token la añadimos una en donde no este
            for token_1 in tokens_no_terminales.difference(set(token)):
                for produccion in producciones[token_1]:
                    if token in produccion:
                        producciones[token_1].append(produccion.remove(token))

    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

def eliminacion_ciclos(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones

