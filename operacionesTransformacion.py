import bisonparse

def eliminacion_no_terminales():
    viejo = []
    nuevo = []

    # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
    # por terminales
    for noTerminal in bisonparse.tokens_no_terminales:
        todo_no_terminales = True
        for produccion in bisonparse.producciones[noTerminal]:
            if produccion is not None:
                for token in produccion:
                    if token not in bisonparse.tokens_terminales:
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
        for noTerminal in bisonparse.tokens_no_terminales:
            todo_no_terminales_o_viejo = True
            for produccion in bisonparse.producciones[noTerminal]:
                if produccion is not None:
                    for token in produccion:
                        if (token not in bisonparse.tokens_terminales) or (token not in viejo):
                            todo_no_terminales_o_viejo = False
                            break
                    if not todo_no_terminales_o_viejo:
                        break

            if todo_no_terminales_o_viejo and noTerminal not in nuevo:
                nuevo.append(noTerminal)

    # producciones se acutualiza a aquellas que esten compuestas por tokenes pertenecientes a nuevo o a terminales
    bisonparse.tokens_terminales = nuevo
    nuevas_reglas = dict()
    for nuevo_no_terminal in nuevo:
        nuevas_producciones = []
        for produccion in bisonparse.producciones[nuevo_no_terminal]:
            todo_terminales_o_nuevo = True
            if produccion is not None:
                for token in produccion:
                    if (token not in bisonparse.tokens_terminales) or (token not in nuevo):
                        todo_terminales_o_nuevo = False
                        break
            if todo_terminales_o_nuevo:
                nuevas_producciones.append(produccion)
        nuevas_reglas[nuevo_no_terminal] = nuevas_producciones

    bisonparse.producciones = nuevas_reglas


def eliminacion_no_accesibles():
    viejo = [bisonparse.token_inicial]
    nuevo = [bisonparse.token_inicial]

    for producciones  in bisonparse.producciones[bisonparse.token_inicial]:
        for token in producciones:
            if (token in bisonparse.tokens_no_terminales or token in bisonparse.tokens_terminales) and token not in nuevo:
                nuevo.append(token)

    while viejo != nuevo:
        viejo = nuevo
        nuevo = viejo
        # Añadimos a nuevo todos los tokens no terminales tales que todas sus produciones esten compuestas
        # por terminales o elementos en viejo
        for tokenViejo in viejo:
            if tokenViejo in token in bisonparse.tokens_no_terminales:
                for producciones in bisonparse.producciones[tokenViejo]:
                    for token in producciones:
                        if (token in bisonparse.tokens_no_terminales or token in bisonparse.tokens_terminales) and token not in nuevo:
                            nuevo.append(token)

    bisonparse.tokens_no_terminales = [value for value in nuevo if value in bisonparse.tokens_no_terminales]
    bisonparse.tokens_terminales = [value for value in nuevo if value in bisonparse.tokens_terminales]

    # producciones se acutualiza a aquellas que esten compuestas por tokenes pertenecientes a nuevo o a terminales
    bisonparse.tokens_terminales = nuevo
    nuevas_reglas = dict()
    for nuevo_no_terminal in nuevo:
        nuevas_producciones = []
        for produccion in bisonparse.producciones[nuevo_no_terminal]:
            todo_terminales_o_nuevo = True
            if produccion is not None:
                for token in produccion:
                    if (token not in bisonparse.tokens_terminales) or (token not in nuevo):
                        todo_terminales_o_nuevo = False
                        break
            if todo_terminales_o_nuevo:
                nuevas_producciones.append(produccion)
        nuevas_reglas[nuevo_no_terminal] = nuevas_producciones

    bisonparse.producciones = nuevas_reglas

def factorizacion_a_izquierda():
    print()


def eliminacion_no_terminables_no_derivables():
    print()

def eliminacion_producciones_epsilon():
    print()

def eliminacion_ciclos():
    print()


def conjunto_primero():
    print()

def conjunto_siguiente():
    print()