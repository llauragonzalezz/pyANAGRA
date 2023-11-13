import itertools
import conjuntos


def removal_unreachable_terminals(start_token, terminal_tokens, non_terminal_tokens, productions):
    old = set()
    new = set(token for production in productions[start_token] if production is not None for token in production) \
            | set(start_token)

    while old != new:
        new_tokens = new.difference(old)
        old = new

        # iteramos sobre los tokens añadidos en la iteración anterior
        for token in new_tokens:
            if token in non_terminal_tokens:
                # añadimos todos los tokens (terminales y no terminales) que se pueden alcanzar desde un token dado
                new |= set(token for production in productions[token] if production is not None for token in production)

    # actualizamos los conjunto de tokens terminales y no terminales a aquellos que sean alcanzables desde el token inicial
    terminal_tokens &= new
    # eliminamos todos los tokens no terminales que no sean alcanzables
    tokens_a_eliminar = non_terminal_tokens.difference(new)
    non_terminal_tokens &= set(token for token in new if token in non_terminal_tokens)

    # dejamos solo las productions que contengan tokens lcanzables desde el token inicial
    productions = {key: value for key, value in productions.items() if key not in tokens_a_eliminar}

    return terminal_tokens, non_terminal_tokens, productions


def non_empty_grammar(start_token, terminal_tokens, non_terminal_tokens, productions):
    _, new_productions = removal_underivable_non_terminals(start_token, terminal_tokens, non_terminal_tokens, productions)
    return productions[start_token] == [[]]


def removal_underivable_non_terminals(start_token, terminal_tokens, non_terminal_tokens, productions):
    old = set(start_token)
    new = set()

    # Añadimos a new todos los tokens que tengan al menos una production compuesta por terminales o epsilon
    for token in non_terminal_tokens:
        for production in productions[token]:
            if production is None or set(production) <= terminal_tokens:
                new |= set(token)

    while old != new:
        old = new
        # Añadimos a new todos los tokens que tengan al menos una production compuesta por tokens terminales o
        # elementos de new o sea una producción epsilon
        for token in non_terminal_tokens:
            for production in productions[token]:
                if production is None or set(production) <= terminal_tokens | old:
                    new |= set(token)

    # Dejamos todas las productions que esten compuestas por elementos de new o tokens terminales
    new_productions = dict()
    for token in new:
        productions_list = []
        for production in productions[token]:
            if production is None or set(production) <= new | terminal_tokens:
                productions_list.append(production)

        new_productions[token] = productions_list

    # In this case, the starting token is underivable, therefore, it produces the empty languaje
    if start_token not in new: 
        new.add(start_token)
        new_productions[start_token] = [[]]

    return new, new_productions


def removal_left_recursion(start_token, non_terminal_tokens, productions):
    nt_tokens = list(non_terminal_tokens)

    # cambiamos la posición del primer elemento para que sea el token inicial
    if nt_tokens.index(start_token) != 0:
        pos_start_token = nt_tokens.index(start_token)
        nt_tokens[pos_start_token], nt_tokens[0] = nt_tokens[0], nt_tokens[pos_start_token]

    # Dada una lista de tokens ponemos sus productions en funcion de tokens que esten anterior a este en la lista
    for i, token_i in enumerate(nt_tokens):
        if i > 0:
            for j, token_j in enumerate(nt_tokens[:i-1]):
                for production in productions[token_i]:
                    # Si el primer token de la producción es un token anterior al de la parte izquierda de la producción
                    # lo sustituimos por todas las producciónes del token
                    if production is not None and production[0] == token_j:
                        productions[token_i].remove(production)
                        for production_to_remplace in productions[token_j]:
                            if production is None:
                                productions[token_i].append(production[1:]) 
                            else:
                                productions[token_i].append(production_to_remplace + production[1:]) 

        # Eliminamos la recursividad a izquierda directa que se haya podido generar
        non_terminal_tokens, productions = removal_direct_left_recursion(token_i, non_terminal_tokens, productions)

    return non_terminal_tokens, productions, nt_tokens

def removal_direct_left_recursion(token, non_terminal_tokens, productions):
    recursive_productions = list()
    non_recursive_productions = list()

    # Hay recursividad a izquierda directa si el primer token de la producción es el mismo que el la parte
    # izquierda de la producción
    for production in productions[token]:
        if production is not None and production[0] == token:
            recursive_productions.append(production[1:])
        else:
            non_recursive_productions.append(production)

    if recursive_productions != []:
        productions[token].clear()
        # Creamos el token que va a eliminar la recursividad a izquierda el token
        name = token + "_rec"
        non_terminal_tokens.add(name)
        productions[name] = [None]

        # Añadimos al new token las produciones con recursividad a izquierda de forma que se convierta en recursividad
        # a derecha
        for regla in recursive_productions:
            productions[name].append(regla + [name])

        # Añadimos a las productions del token las reglas que no tenian recuersividad
        for regla in non_recursive_productions:
            productions[token].append(regla + [name])
    return non_terminal_tokens, productions


# Un token es nullable si y solo si este puede alcanzar una producción epsilon a partir de derivar sus productions
def is_nullable(token, terminal_tokens, non_terminal_tokens, productions):
    if None in productions[token]:
        return True

    for production in productions[token]:
        if None in conjuntos.calculate_first_set_sentence(production, token, terminal_tokens, non_terminal_tokens, productions):
            return True

    return False



def removal_epsilon_productions(terminal_tokens, non_terminal_tokens, productions):
    # Calculamos el conjunto de tokens nullables
    nullable_tokens = {token for token in non_terminal_tokens if is_nullable(token, terminal_tokens, non_terminal_tokens, productions)}
    for token in non_terminal_tokens:
        if token in nullable_tokens and None in productions[token]:
            productions[token].remove(None)  # quitamos la production epsilon

        for production in productions[token]:
            # Obtenemos los tokens nullables dentro de la producción
            nullable_tokens_production = set(production) & nullable_tokens
            indexs_token_nullable = {production.index(null_token) for null_token in nullable_tokens_production}
            combinaciones = []

            # Creamos todas las combinaciones posibles de los indexs de tokenes nullables
            for i in range(1, len(indexs_token_nullable) + 1):
                combinaciones.extend(list(x) for x in itertools.combinations(indexs_token_nullable, i))

            if len(nullable_tokens_production) == len(production):
                combinaciones.remove([*range(len(production))])


            # Añadimos al token todas las combinaciones posibles de las apariciones de los tokens nullables de la producción
            for lista in combinaciones:
                nueva_production = [x for i, x in enumerate(production) if i not in lista]
                # Añadimos todas las productions (no epsilon) que no esten en las productions del token
                # El único token que puede tener una producción epsilon es el token inicial en el caso de que la cadena
                # vácia pertenezca al lenguaje
                if nueva_production not in productions[token]:
                    productions[token].append(nueva_production)

    return productions


def tokens_unitarios_alanzables(token, terminal_tokens, non_terminal_tokens, productions):
    old = set()
    new = set()
    # Añadimos todos los tokens que sean producción unitaria de un token
    for production in productions[token]:
        if production is not None and len(production) == 1 and production[0] in non_terminal_tokens:
            productions[token].remove(production) # Eliminamos la producción unitaria
            new.add(production[0])

    while old != new:
        new_tokens = new.difference(old)
        old = new.copy()

        # Iteramos sobre los tokens añadidos en la utlima iteración
        for token1 in new_tokens:
            added = False

            for production in productions[token1]:
                # Añadimos todas las poduccion unitaria que se puedan alcanzar desde un token
                if production is not None and len(production) == 1 and production[0] in non_terminal_tokens:
                    new.add(production[0])
                elif not added:
                    added = True
                    # Para que la gramática sea equivalente trás eliminar la producción unitaria es necesario añadir
                    # todas las productions(no unitarias) del token de la producción unitaria
                    for production_to_add in productions[token1]:
                        if (len(production_to_add) > 1 or (len(production_to_add) == 1 and production_to_add[0] in terminal_tokens)) and production_to_add not in productions[token]:
                            productions[token].append(production_to_add)

    return productions


def removal_cycles(terminal_tokens, non_terminal_tokens, productions):
    # Eliminamos las productions no unitarias de cada token, eliminando así los posibles ciclos produciadas por estas
    for token in non_terminal_tokens:
        productions = tokens_unitarios_alanzables(token, terminal_tokens, non_terminal_tokens, productions)

    return productions

def removal_nonsolitary_terminals(terminal_tokens, non_terminal_tokens, productions):
    for token in terminal_tokens:
        name = "token_" + token
        productions[name] = [[token]]
        non_terminal_tokens.add(name)

    for token in non_terminal_tokens:
        for production in productions[token]:
            if production is not None and len(production) > 1:
                for index, token_prod in enumerate(production):
                    if token_prod in terminal_tokens:
                        production[index] = "token_" + token_prod

    return non_terminal_tokens, productions


def agrupar_productions_pares(non_terminal_tokens, productions):
    chomsky_index = 1
    nt_tokens = non_terminal_tokens.copy()
    for token in non_terminal_tokens:
        for index, production in enumerate(productions[token]):
            if production is not None and len(production) > 2:
                new_production = "Chom_"+str(chomsky_index)
                chomsky_index += 1
                nt_tokens.add(new_production)
                productions[token][index] = [production[0], new_production]
                last_token = new_production
                for token_prod in production[1:-2]:
                    new_production = "Chom_" + str(chomsky_index)
                    chomsky_index += 1
                    nt_tokens.add(new_production)
                    productions[last_token] = [[token_prod, new_production]]
                    last_token = new_production
                productions[last_token] = [production[-2:]]

    return nt_tokens, productions


def chomsky_normal_form(start_token, terminal_tokens, non_terminal_tokens, productions):
    # Step 1: remove epilon productions
    productions = removal_epsilon_productions(start_token, terminal_tokens, non_terminal_tokens, productions)
    # Step 2: remove cycles
    productions = removal_cycles(terminal_tokens, non_terminal_tokens, productions)
    # Step 3: remove left recursion
    non_terminal_tokens, productions, _ = removal_left_recursion(start_token, non_terminal_tokens, productions)
    # Step 4: remove un
    non_terminal_tokens, productions = removal_nonsolitary_terminals(terminal_tokens, non_terminal_tokens, productions)
    # Step 5:
    non_terminal_tokens, productions = agrupar_productions_pares(non_terminal_tokens, productions)

    return non_terminal_tokens, productions


def left_factoring(non_terminal_tokens, productions):
    old_non_terminal_tokens = non_terminal_tokens
    for token in old_non_terminal_tokens:
        old_productions = productions[token].copy()
        times = 1
        for production in old_productions:
            if production in productions[token] and production is not None and len(productions[token]) > 1: # sino esta es que se ha reducido en alguna iteracion anterior
                non_terminal_tokens, productions, times = find_prefix(production, productions[token], token, non_terminal_tokens, productions, times, "_" + str(times))

    return non_terminal_tokens, productions


# cadenas_differents si y solo si la cadena es una producción epsilon o si la cadena y la de referencia no comienzan por
# el mismo token
def different_productions(reference_string, cadena):
    return cadena is None or cadena == [] or reference_string[0] != cadena[0]

#
def find_prefix(reference_string, new_productions, name_prod, non_terminal_tokens, productions, times, sufix):
    prefix_productions = list()
    different = False
    for index, caracter in enumerate(reference_string):
        for new_production in new_productions:
            # En el momento en el que cadenas que no son differents dejan de coincidir se ha calulado el prefijo común
            if not different_productions(reference_string, new_production) and (len(new_production) < index + 1 or caracter != new_production[index]):
                different = True
            elif not different_productions(reference_string, new_production) and caracter == new_production[index] and new_production not in prefix_productions:
                prefix_productions.append(new_production)

        if prefix_productions == []:  # No hay prefijo común
            return non_terminal_tokens, productions, times

        if different: # Left factorice
            # Añadimos un token no terminal el cual agrupe todas las productions con sufijo comun
            name = name_prod + sufix
            sufix = "'"
            # Las productions del new token contienen todas las cadenas comunes sin el prefijo
            productions[name] = [prod[index:] for prod in prefix_productions]
            non_terminal_tokens.add(name)
            # Sustituimos las productions con prefijo por una que sea el prefijo + new token
            new_productions.append(reference_string[:index] + [name])
            for prefix_prod in prefix_productions:
                new_productions.remove(prefix_prod)

            productions[name_prod] = new_productions
            # Factorizamos a izquierda ahora sobre el new token
            non_terminal_tokens, productions, _ = find_prefix(productions[name][0], productions[name], name, non_terminal_tokens, productions, 0, sufix)
            return non_terminal_tokens, productions, times + 1

    return non_terminal_tokens, productions, times


def greibach_normal_form(start_token, non_terminal_tokens, productions):
    # Step 1: remove left recursion
    non_terminal_tokens, new_productions, nt_tokens = removal_left_recursion(start_token, non_terminal_tokens, productions)

    # En el orden inverso al elegido para eliminar la recursividad a izquierda eliminamos todas las productions que
    # empiecen por no terminal
    for token in reversed(nt_tokens):
        productions_to_remove = []
        for production in productions[token]:
            if production is not None and production[0] in non_terminal_tokens:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in productions[production[0]]:
                    if production_to_remplace is None:
                        new_productions[token].append(production[1:])
                    else:
                        new_productions[token].append(production_to_remplace + production[1:])

        for production in productions_to_remove:
            new_productions[token].remove(production)

    # Eliminamos todas las productions que empiecen por no terminal de los tokens que se han añadido a la hora de
    # eliminar la recursividad a izquierda
    new_tokens = non_terminal_tokens.difference(set(nt_tokens))
    for token in new_tokens:
        productions_to_remove = []
        for production in productions[token]:
            if production is not None and production[0] in non_terminal_tokens:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in productions[production[0]]:
                    new_productions[token].append(production_to_remplace + production[1:])
        for production in productions_to_remove:
            new_productions[token].remove(production)

    return non_terminal_tokens, new_productions
