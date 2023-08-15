import itertools


def eliminacion_simbolos_inutiles(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set()

    nuevo = set(token for produccion in producciones[token_inicial] if produccion is not None for token in produccion) \
            | set(token_inicial)

    while viejo != nuevo:
        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo

        # iteramos sobre los tokens añadidos en la iteración anterior
        for token in nuevos_token:
            if token in tokens_no_terminales:
                # añadimos todos los tokens (terminales y no terminales) que se pueden alcanzar desde un token dado
                nuevo |= set(token for produccion in producciones[token] if produccion is not None for token in produccion)

    # actualizamos los conjunto de tokens terminales y no terminales a aquellos que sean alcanzables desde el token inicial
    tokens_terminales &= nuevo
    # eliminamos todos los tokens no terminales que no sean alcanzables
    tokens_a_eliminar = tokens_no_terminales.difference(nuevo)
    tokens_no_terminales &= set(token for token in nuevo if token in tokens_no_terminales)

    # dejamos solo las producciones que contengan tokens lcanzables desde el token inicial
    producciones = {clave: valor for clave, valor in producciones.items() if clave not in tokens_a_eliminar}

    return tokens_terminales, tokens_no_terminales, producciones


def gramatica_no_vacia(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    _, nuevas_producciones = eliminacion_simolos_no_termibales(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    return token_inicial in nuevas_producciones


def eliminacion_simolos_no_termibales(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set(token_inicial)
    nuevo = set()

    # Añadimos a nuevo todos los tokens que tengan al menos una produccion compuesta por terminales o epsilon
    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            if produccion is None or set(produccion) <= tokens_terminales:
                nuevo |= set(token)

    while viejo != nuevo:
        viejo = nuevo
        # Añadimos a nuevo todos los tokens que tengan al menos una produccion compuesta por tokens terminales o
        # elementos de nuevo o sea una producción epsilon
        for token in tokens_no_terminales:
            for produccion in producciones[token]:
                if produccion is None or set(produccion) <= tokens_terminales | viejo:
                    nuevo |= set(token)

    # Dejamos todas las producciones que esten compuestas por elementos de nuevo o tokens terminales
    nuevas_producciones = dict()
    for token in nuevo:
        lista_producciones = []
        for produccion in producciones[token]:
            if produccion is None or set(produccion) <= nuevo | tokens_terminales:
                lista_producciones.append(produccion)

        nuevas_producciones[token] = lista_producciones

    return nuevo, nuevas_producciones


def eliminar_recursividad_izquierda(token_inicial, tokens_no_terminales, producciones):
    tokens_nt = list(tokens_no_terminales)

    # cambiamos la posición del primer elemento para que sea el token inicial
    if tokens_nt.index(token_inicial) != 0:
        pos_token_inicial = tokens_nt.index(token_inicial)
        tokens_nt[pos_token_inicial], tokens_nt[0] = tokens_nt[0], tokens_nt[pos_token_inicial]

    # Dada una lista de tokens ponemos sus producciones en funcion de tokens que esten anterior a este en la lista
    for i, token_i in enumerate(tokens_nt):
        if i > 0:
            for j, token_j in enumerate(tokens_nt[:i-1]):
                for produccion in producciones[token_i]:
                    # Si el primer token de la producción es un token anterior al de la parte izquierda de la producción
                    # lo sustituimos por todas las producciónes del token
                    if produccion is not None and produccion[0] == token_j:
                        producciones[token_i].remove(produccion)
                        for produccion_remplazar in producciones[token_j]:
                            producciones[token_i].append(produccion_remplazar + produccion[1:])

        # Eliminamos la recursividad a izquierda directa que se haya podido generar
        tokens_no_terminales, producciones = eliminar_recursividad_izquierda_directa(token_i, tokens_no_terminales, producciones)

    return tokens_no_terminales, producciones, tokens_nt

def eliminar_recursividad_izquierda_directa(token, tokens_no_terminales, producciones):
    reglas_recursivas = list()
    reglas_no_recursivas = list()

    # Hay recursividad a izquierda directa si el primer token de la producción es el mismo que el la parte
    # izquierda de la producción
    for produccion in producciones[token]:
        if produccion is not None and produccion[0] == token:
            reglas_recursivas.append(produccion[1:])
        else:
            reglas_no_recursivas.append(produccion)

    if reglas_recursivas != []:
        producciones[token].clear()
        # Creamos el token que va a eliminar la recursividad a izquierda el token
        nombre = token + "_rec"
        tokens_no_terminales.add(nombre)
        producciones[nombre] = [None]

        # Añadimos al nuevo token las produciones con recursividad a izquierda de forma que se convierta en recursividad
        # a derecha
        for regla in reglas_recursivas:
            producciones[nombre].append(regla + [nombre])

        # Añadimos a las producciones del token las reglas que no tenian recuersividad
        for regla in reglas_no_recursivas:
            producciones[token].append(regla + [nombre])
    return tokens_no_terminales, producciones


# Un token es nullable si y solo si este puede alcanzar una producción epsilon a partir de derivar sus producciones
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
                print("tokens a añadir: ", [token1 for produccion in producciones[token1] for token1 in produccion])
                nuevo |= set(token1 for produccion in producciones[token1] for token1 in produccion)
                print(nuevo)
    return False

def eliminacion_producciones_epsilon(token_inicial, tokens_no_terminales, producciones):
    # Calculamos el conjunto de tokens nullables
    nullable_tokens = {token for token in tokens_no_terminales if is_nullable(token, tokens_no_terminales, producciones)}

    for token in tokens_no_terminales:
        if token in nullable_tokens:
            producciones[token].remove(None)  # quitamos la produccion epsilon

        for produccion in producciones[token]:
            # Obtenemos los tokens nullables dentro de la producción
            nullable_tokens_produccion = set(produccion) & nullable_tokens
            indices_token_nullable = {produccion.index(null_token) for null_token in nullable_tokens_produccion}
            combinaciones = []

            # Creamos todas las combinaciones posibles de los indices de tokenes nullables
            for i in range(1, len(indices_token_nullable) + 1):
                combinaciones.extend(list(x) for x in itertools.combinations(indices_token_nullable, i))

            # Añadimos al token todas las combinaciones posibles de las apariciones de los tokens nullables de la producción
            for lista in combinaciones:
                nueva_produccion = [x for i, x in enumerate(produccion) if i not in lista]
                # Añadimos todas las producciones (no epsilon) que no esten en las producciones del token
                # El único token que puede tener una producción epsilon es el token inicial en el caso de que la cadena
                # vácia pertenezca al lenguaje
                if (nueva_produccion != [] or (nueva_produccion == [] and token == token_inicial)) and nueva_produccion not in producciones[token]:
                    producciones[token].append(nueva_produccion)

    return producciones


def tokens_unitarios_alanzables(token, tokens_terminales, tokens_no_terminales, producciones):
    viejo = set()
    nuevo = set()
    # Añadimos todos los tokens que sean producción unitaria de un token
    for produccion in producciones[token]:
        if produccion is not None and len(produccion) == 1 and produccion[0] in tokens_no_terminales:
            producciones[token].remove(produccion) # Eliminamos la producción unitaria
            nuevo.add(produccion[0])

    while viejo != nuevo:
        nuevos_token = nuevo.difference(viejo)
        viejo = nuevo.copy()

        # Iteramos sobre los tokens añadidos en la utlima iteración
        for token1 in nuevos_token:
            aniadido = False

            for produccion in producciones[token1]:
                # Añadimos todas las poduccion unitaria que se puedan alcanzar desde un token
                if produccion is not None and len(produccion) == 1 and produccion[0] in tokens_no_terminales:
                    nuevo.add(produccion[0])
                elif not aniadido:
                    aniadido = True
                    # Para que la gramática sea equivalente trás eliminar la producción unitaria es necesario añadir
                    # todas las producciones(no unitarias) del token de la producción unitaria
                    for produccion_aniadir in producciones[token1]:
                        if (len(produccion_aniadir) > 1 or (len(produccion_aniadir) == 1 and produccion_aniadir[0] in tokens_terminales)) and produccion_aniadir not in producciones[token]:
                            producciones[token].append(produccion_aniadir)

    return producciones


def eliminacion_producciones_unitarias(tokens_terminales, tokens_no_terminales, producciones):
    # Eliminamos las producciones no unitarias de cada token, eliminando así los posibles ciclos produciadas por estas
    for token in tokens_no_terminales:
        producciones = tokens_unitarios_alanzables(token, tokens_terminales, tokens_no_terminales, producciones)

    return producciones

def reorganizacion_producciones(produccion, tokens_no_terminales, producciones, indice_chomsky):
    if len(produccion) > 2:
        tokens_no_terminales.add("Chom_" + indice_chomsky)
        producciones["Chom_" + indice_chomsky] = produccion[0] + ["Chom_" + (indice_chomsky+1)]
        indice_chomsky += 1
        tokens_no_terminales, producciones, indice_chomsky = reorganizacion_producciones(produccion[1:], tokens_no_terminales, producciones, indice_chomsky+1)
    return tokens_no_terminales, producciones, indice_chomsky


def agrupar_producciones_pares(tokens_terminales, tokens_no_terminales, producciones):
    for token in tokens_terminales:
        nombre = "token_" + token
        producciones[nombre] = [token]

    indice_chomsky = 1
    for token in tokens_no_terminales:
        for produccion in producciones[token]:
            for index, token in enumerate(produccion):
                if token in tokens_no_terminales:
                    produccion.remplace(token, "token_"+token)
            if len(produccion) > 2:
                indice_chomsky_aux = indice_chomsky
                tokens_no_terminales, producciones, indice_chomsky = reorganizacion_producciones(produccion[1:], tokens_no_terminales, producciones, indice_chomsky)
                produccion = produccion[0] + ["Chom_" + indice_chomsky_aux]

    return tokens_no_terminales, producciones


def forma_normal_chomsky(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    tokens_no_terminales, producciones = eliminacion_producciones_epsilon(token_inicial, tokens_no_terminales, producciones)
    tokens_no_terminales, producciones = eliminacion_producciones_unitarias(tokens_no_terminales, producciones)
    tokens_no_terminales, producciones, _ = eliminar_recursividad_izquierda(token_inicial, tokens_no_terminales, producciones)
    tokens_no_terminales, producciones = agrupar_producciones_pares(tokens_terminales, tokens_no_terminales, producciones)
    return token_inicial, tokens_terminales, tokens_no_terminales, producciones


def factorizacion_izquierda(tokens_no_terminales, producciones):
    tokens_no_terminales_antiguos = tokens_no_terminales.copy()
    for token in tokens_no_terminales_antiguos:
        producciones_antiguas = producciones[token].copy()
        veces = 1
        for produccion in producciones_antiguas:
            if produccion in producciones[token] and produccion is not None and len(producciones[token]) > 1: # sino esta es que se ha reducido en alguna iteracion anterior
                tokens_no_terminales, producciones, veces = encontrar_prefijos(produccion, producciones[token], token, tokens_no_terminales, producciones, veces, "_" + str(veces))

    return tokens_no_terminales, producciones


# cadenas_diferentes si y solo si la cadena es una producción epsilon o si la cadena y la de referencia no comienzan por
# el mismo token
def cadenas_diferentes(cadena_referencia, cadena):
    return cadena is None or cadena == [] or cadena_referencia[0] != cadena[0]

#
def encontrar_prefijos(cadena_referencia, cadenas, nombre_prod, tokens_no_terminales, producciones, veces, sufijo):
    cadenas_comunes = list()
    diferente = False
    for indice, caracter in enumerate(cadena_referencia):
        for cadena in cadenas:
            # En el momento en el que cadenas que no son diferentes dejan de coincidir se ha calulado el prefijo común
            if not cadenas_diferentes(cadena_referencia, cadena) and (len(cadena) < indice + 1 or caracter != cadena[indice]):
                diferente = True
            elif not cadenas_diferentes(cadena_referencia, cadena) and caracter == cadena[indice] and cadena not in cadenas_comunes:
                cadenas_comunes.append(cadena)

        if cadenas_comunes == []:  # No hay prefijo común
            return tokens_no_terminales, producciones, veces

        if diferente: # Factorizamos a izquierda
            # Añadimos un token no terminal el cual agrupe todas las producciones con sufijo comun
            nombre = nombre_prod + sufijo
            sufijo = "'"
            # Las producciones del nuevo token contienen todas las cadenas comunes sin el prefijo
            producciones[nombre] = [prod[indice:] for prod in cadenas_comunes]
            tokens_no_terminales.add(nombre)
            # Sustituimos las producciones con prefijo por una que sea el prefijo + nuevo token
            cadenas.append(cadena_referencia[:indice] + [nombre])
            for cadena_comun in cadenas_comunes:
                cadenas.remove(cadena_comun)

            producciones[nombre_prod] = cadenas
            # Factorizamos a izquierda ahora sobre el nuevo token
            tokens_no_terminales, producciones, _ = encontrar_prefijos(producciones[nombre][0], producciones[nombre], nombre, tokens_no_terminales, producciones, 0, sufijo)
            return tokens_no_terminales, producciones, veces + 1

    return tokens_no_terminales, producciones, veces


def forma_normal_greibach(token_inicial, tokens_no_terminales, producciones):
    # Paso 1: eliminamos la recursividad a izquierda
    tokens_no_terminales, producciones_nuevas, tokens_nt = eliminar_recursividad_izquierda(token_inicial, tokens_no_terminales, producciones)

    # En el orden inverso al elegido para eliminar la recursividad a izquierda eliminamos todas las producciones que
    # empiecen por no terminal
    for token in reversed(tokens_nt):
        producciones_a_eliminar = []
        for produccion in producciones[token]:
            if produccion is not None and produccion[0] in tokens_no_terminales:
                producciones_a_eliminar.append(produccion)
                # Sustituimos en la producción el primer token por todas las producciones que tiene
                for produccion_remplazar in producciones[produccion[0]]:
                    producciones_nuevas[token].append(produccion_remplazar + produccion[1:])

        for produccion in producciones_a_eliminar:
            producciones_nuevas[token].remove(produccion)

    # Eliminamos todas las producciones que empiecen por no terminal de los tokens que se han añadido a la hora de
    # eliminar la recursividad a izquierda
    tokens_nuevos = tokens_no_terminales.difference(set(tokens_nt))
    for token in tokens_nuevos:
        producciones_a_eliminar = []
        for produccion in producciones[token]:
            if produccion is not None and produccion[0] in tokens_no_terminales:
                producciones_a_eliminar.append(produccion)
                # Sustituimos en la producción el primer token por todas las producciones que tiene
                for produccion_remplazar in producciones[produccion[0]]:
                    producciones_nuevas[token].append(produccion_remplazar + produccion[1:])
        for produccion in producciones_a_eliminar:
            producciones_nuevas[token].remove(produccion)

    return tokens_no_terminales, producciones_nuevas
