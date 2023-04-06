import itertools
#buscar libreria para arboles bianrios

# a las 11:30

# mirar menus
# conjutno primero y siguiete, tabla
# simular la entrada


# precudicion, elementos,
# postcondicion

# ventana o pestaña(que se pueda desacoplar)

# fichero temporal oculto

# poner un parametro de invocacion, para que si se pone la entrada sea stdin

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


def eliminar_recursividad_izquierda(tokens_no_terminales, producciones):
    tokens_nt = list(tokens_no_terminales)
    for i, token_i in enumerate(tokens_nt):
        if i > 0:
            for j, token_j in enumerate(tokens_nt[:i-1]):
                for produccion in producciones[token_i]:
                    if produccion is not None and produccion[0] == token_j:
                        producciones[token_i].remove(produccion)
                        for produccion_remplazar in producciones[token_j]:
                            producciones[token_i].append(produccion_remplazar + produccion[1:])
        tokens_no_terminales, producciones = eliminar_recursividad_izquierda_directa(token_i, tokens_no_terminales, producciones)
    return tokens_no_terminales, producciones

def eliminar_recursividad_izquierda_directa(token, tokens_no_terminales, producciones):
    reglas_recursivas = list()
    reglas_no_recursivas = list()
    for produccion in producciones[token]:
        if produccion is not None and produccion[0] == token:
            reglas_recursivas.append(produccion[1:])
        else:
            reglas_no_recursivas.append(produccion)
    if reglas_recursivas != []:
        producciones[token].clear()
        nombre = token + "_rec"
        tokens_no_terminales.add(nombre)
        producciones[nombre] = [[]]
        for regla in reglas_recursivas:
            producciones[nombre].append(regla + [nombre])
        for regla in reglas_no_recursivas:
            producciones[token].append(regla + [nombre])
    return tokens_no_terminales, producciones

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
#graybag -> wikipedia

def eliminacion_producciones_unitarias(tokens_terminales, tokens_no_terminales, producciones):

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
    tokens_no_terminales, producciones = eliminacion_producciones_epsilon(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    tokens_no_terminales, producciones = eliminacion_producciones_unitarias(tokens_no_terminales, producciones)
    tokens_no_terminales, producciones = eliminar_recursividad_izquierda(tokens_no_terminales, producciones)
    tokens_no_terminales, producciones = agrupar_producciones_pares(tokens_terminales, tokens_no_terminales, producciones)
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


def factorizacion_izquierda(tokens_no_terminales, producciones):
    tokens_no_terminales_antiguos = tokens_no_terminales.copy()
    for token in tokens_no_terminales_antiguos:
        producciones_antiguas = producciones[token].copy()
        veces = 1
        for produccion in producciones_antiguas:
            if produccion in producciones[token] and produccion is not None and len(producciones[token]) > 1: # sino esta es que se ha reducido en alguna iteracion anterior
                tokens_no_terminales, producciones, veces = encontrar_prefijos(produccion, producciones[token], token, tokens_no_terminales, producciones, veces, "_" + str(veces))

    return tokens_no_terminales, producciones


def cadenas_diferentes(cadena_referencia, cadena):
    return cadena is None or cadena == [] or cadena_referencia[0] != cadena[0]


def encontrar_prefijos(cadena_referencia, cadenas, nombre_prod, tokens_no_terminales, producciones, veces, sufijo):
    cadenas_comunes = list()
    diferente = False
    for indice, caracter in enumerate(cadena_referencia):
        for cadena in cadenas:
            if not cadenas_diferentes(cadena_referencia, cadena) and (len(cadena) < indice + 1 or caracter != cadena[indice]):
                diferente = True
            elif not cadenas_diferentes(cadena_referencia, cadena) and caracter == cadena[indice] and cadena not in cadenas_comunes:
                cadenas_comunes.append(cadena)

        if cadenas_comunes == []:
            return tokens_no_terminales, producciones, veces

        if diferente:
            nombre = nombre_prod + sufijo
            sufijo = "'"
            producciones[nombre] = [prod[indice:] for prod in cadenas_comunes]
            tokens_no_terminales.add(nombre)
            cadenas.append(cadena_referencia[:indice] + [nombre])
            for cadena_comun in cadenas_comunes: # elimino las producciones comunes
                cadenas.remove(cadena_comun)
            producciones[nombre_prod] = cadenas
            tokens_no_terminales, producciones, _ = encontrar_prefijos(producciones[nombre][0], producciones[nombre], nombre, tokens_no_terminales, producciones, 0, sufijo)
            return tokens_no_terminales, producciones, veces + 1

    return tokens_no_terminales, producciones, veces



def forma_normal_greibach(tokens_no_terminales, producciones):

    return tokens_no_terminales, producciones
