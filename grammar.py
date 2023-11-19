"""
Filename:
Author: Laura González Pizarro
Description:
"""
import copy
import itertools
import conjuntos


class Grammar:

    def __init__(self, initial_token, terminals, non_terminals, productions):
        self.initial_token = initial_token
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.productions = productions

    def copy(self):
        return Grammar(self.initial_token, self.terminals.copy(), self.non_terminals.copy(), copy.deepcopy(self.productions))


def removal_unreachable_terminals(grammar):
    gr = grammar.copy()
    old = set()
    new = set(symbol for production in gr.productions[gr.initial_token] if production is not None for symbol in production) \
            | set(gr.initial_token)

    while old != new:
        new_symbols = new.difference(old)
        old = new

        # iteramos sobre los tokens añadidos en la iteración anterior
        for token in new_symbols:
            if token in gr.non_terminals:
                # añadimos todos los tokens (terminales y no terminales) que se pueden alcanzar desde un token dado
                new |= set(token for production in gr.productions[token] if production is not None for token in production)

    # actualizamos los conjunto de tokens terminales y no terminales a aquellos que sean alcanzables desde el token inicial
    gr.terminals &= new
    # eliminamos todos los tokens no terminales que no sean alcanzables
    tokens_a_eliminar = gr.non_terminals.difference(new)
    gr.non_terminals &= set(token for token in new if token in gr.non_terminals)

    # dejamos solo las productions que contengan tokens lcanzables desde el token inicial
    gr.productions = {key: value for key, value in gr.productions.items() if key not in tokens_a_eliminar}

    return gr


def non_empty_grammar(initial_token, terminals, non_terminals, productions):
    _, new_productions = removal_underivable_non_terminals(initial_token, terminals, non_terminals, productions)
    return productions[initial_token] == [[]]


def removal_underivable_non_terminals(grammar):
    gr = grammar.copy()

    old = set(gr.initial_token)
    new = set()

    # Añadimos a new todos los tokens que tengan al menos una production compuesta por terminales o epsilon
    for token in gr.non_terminals:
        for production in gr.productions[token]:
            if production is None or set(production) <= gr.terminals:
                new |= set(token)

    while old != new:
        old = new
        # Añadimos a new todos los tokens que tengan al menos una production compuesta por tokens terminales o
        # elementos de new o sea una producción epsilon
        for token in gr.non_terminals:
            for production in gr.productions[token]:
                if production is None or set(production) <= gr.terminals | old:
                    new |= set(token)

    # Dejamos todas las productions que esten compuestas por elementos de new o tokens terminales
    new_productions = dict()
    for token in new:
        productions_list = []
        for production in gr.productions[token]:
            if production is None or set(production) <= new | gr.terminals:
                productions_list.append(production)

        new_productions[token] = productions_list

    # In this case, the initial token is underivable, therefore, it produces the empty languaje
    if gr.initial_token not in new:
        new.add(gr.initial_token)
        new_productions[gr.initial_token] = [[]]

    return Grammar(gr.initial_token, gr.terminals, new, new_productions)


def removal_left_recursion(grammar):
    gr = grammar.copy()

    nt_symbols = list(gr.non_terminals)

    # cambiamos la posición del primer elemento para que sea el token inicial
    if nt_symbols.index(gr.initial_token) != 0:
        pos_initial_token = nt_symbols.index(gr.initial_token)
        nt_symbols[pos_initial_token], nt_symbols[0] = nt_symbols[0], nt_symbols[pos_initial_token]

    # Dada una lista de tokens ponemos sus productions en funcion de tokens que esten anterior a este en la lista
    for i, symbol_i in enumerate(nt_symbols):
        if i > 0:
            for j, symbol_j in enumerate(nt_symbols[:i-1]):
                for production in gr.productions[symbol_i]:
                    # Si el primer token de la producción es un token anterior al de la parte izquierda de la producción
                    # lo sustituimos por todas las producciónes del token
                    if production is not None and production[0] == symbol_j:
                        gr.productions[symbol_i].remove(production)
                        for production_to_remplace in gr.productions[symbol_j]:
                            if production is None:
                                gr.productions[symbol_i].append(production[1:])
                            else:
                                gr.productions[symbol_i].append(production_to_remplace + production[1:])

        # Eliminamos la recursividad a izquierda directa que se haya podido generar
        gr = removal_direct_left_recursion(gr, symbol_i)

    return gr, nt_symbols


def removal_direct_left_recursion(grammar, sysmbol):
    gr = grammar.copy()
    recursive_productions = list()
    non_recursive_productions = list()

    # Hay recursividad a izquierda directa si el primer token de la producción es el mismo que el la parte
    # izquierda de la producción
    for production in gr.productions[sysmbol]:
        if production is not None and production[0] == sysmbol:
            recursive_productions.append(production[1:])
        else:
            non_recursive_productions.append(production)

    if recursive_productions != []:
        gr.productions[sysmbol].clear()
        # Creamos el token que va a eliminar la recursividad a izquierda el token
        name = sysmbol + "_rec"
        gr.non_terminals.add(name)
        gr.productions[name] = [None]

        # Añadimos al new token las produciones con recursividad a izquierda de forma que se convierta en recursividad
        # a derecha
        for prod in recursive_productions:
            gr.productions[name].append(prod + [name])

        # Añadimos a las productions del token las reglas que no tenian recuersividad
        for prod in non_recursive_productions:
            gr.productions[sysmbol].append(prod + [name])

    return gr


# Un token es nullable si y solo si este puede alcanzar una producción epsilon a partir de derivar sus productions
def is_nullable(gr, token):
    if None in gr.productions[token]:
        return True

    for production in gr.productions[token]:
        if None in conjuntos.calculate_first_set_sentence(production, token, gr.terminals, gr.non_terminals, gr.productions):
            return True

    return False



def removal_epsilon_productions(grammar):
    gr = grammar.copy()

    # Calculamos el conjunto de tokens nullables
    nullable_tokens = {symbol for symbol in gr.non_terminals if is_nullable(gr, symbol)}
    for symbol in gr.non_terminals:
        if symbol in nullable_tokens and None in gr.productions[symbol]:
            gr.productions[symbol].remove(None)  # quitamos la production epsilon

        for production in gr.productions[symbol]:
            # Obtenemos los tokens nullables dentro de la producción
            nullable_tokens_production = set(production) & nullable_tokens
            indexs_token_nullable = {production.index(null_token) for null_token in nullable_tokens_production}
            combinations = []

            # Creamos todas las combinaciones posibles de los indexs de tokenes nullables
            for i in range(1, len(indexs_token_nullable) + 1):
                combinations.extend(list(x) for x in itertools.combinations(indexs_token_nullable, i))

            if len(nullable_tokens_production) == len(production):
                combinations.remove([*range(len(production))])

            # Añadimos al token todas las combinaciones posibles de las apariciones de los tokens nullables de la producción
            for combination in combinations:
                new_production = [x for i, x in enumerate(production) if i not in combination]
                # Añadimos todas las productions (no epsilon) que no esten en las productions del token
                # El único token que puede tener una producción epsilon es el token inicial en el caso de que la cadena
                # vácia pertenezca al lenguaje
                if new_production not in gr.productions[symbol]:
                    gr.productions[symbol].append(new_production)

    return gr


def remove_unit_productions(grammar, symbol):
    gr = grammar.copy()

    old = set()
    new = set()
    # Añadimos todos los tokens que sean producción unitaria de un token
    for production in gr.productions[symbol]:
        if production is not None and len(production) == 1 and production[0] in gr.non_terminals:
            gr.productions[symbol].remove(production) # delete unit production
            new.add(production[0])

    while old != new:
        new_symbols = new.difference(old)
        old = new.copy()

        # Iteramos sobre los tokens añadidos en la utlima iteración
        for new_symbol in new_symbols:
            added = False

            for production in gr.productions[new_symbol]:
                # Añadimos todas las poduccion unitaria que se puedan alcanzar desde un token
                if production is not None and len(production) == 1 and production[0] in gr.non_terminals:
                    new.add(production[0])
                elif not added:
                    added = True
                    # Para que la gramática sea equivalente trás eliminar la producción unitaria es necesario añadir
                    # todas las productions(no unitarias) del token de la producción unitaria
                    for production_to_add in gr.productions[new_symbol]:
                        if (len(production_to_add) > 1 or (len(production_to_add) == 1 and production_to_add[0] in gr.terminals)) and production_to_add not in gr.productions[symbol]:
                            gr.productions[symbol].append(production_to_add)

    return gr


def removal_cycles(grammar):
    gr = grammar.copy()

    # Eliminamos las productions no unitarias de cada token, eliminando así los posibles ciclos produciadas por estas
    for symbol in gr.non_terminals:
        gr = remove_unit_productions(gr, symbol)

    return gr

def removal_nonsolitary_terminals(grammar):
    gr = grammar.copy()

    for token in gr.terminals:
        name = "token_" + token
        gr.productions[name] = [[token]]
        gr.non_terminals.add(name)

    for token in gr.non_terminals:
        for production in gr.productions[token]:
            if production is not None and len(production) > 1:
                for index, token_prod in enumerate(production):
                    if token_prod in gr.terminals:
                        production[index] = "token_" + token_prod

    return gr


def agrupar_productions_pares(grammar):
    gr = grammar.copy()

    chomsky_index = 1
    nt_tokens = gr.non_terminals.copy()
    for symbol in gr.non_terminals:
        for index, production in enumerate(gr.productions[symbol]):
            if production is not None and len(production) > 2:
                new_production = "Chom_"+str(chomsky_index)
                chomsky_index += 1
                nt_tokens.add(new_production)
                gr.productions[symbol][index] = [production[0], new_production]
                last_symbol = new_production
                for token_prod in production[1:-2]:
                    new_production = "Chom_" + str(chomsky_index)
                    chomsky_index += 1
                    nt_tokens.add(new_production)
                    gr.productions[last_symbol] = [[token_prod, new_production]]
                    last_symbol = new_production
                gr.productions[last_symbol] = [production[-2:]]

    return Grammar(gr.initial_token, gr.terminals, nt_tokens, gr.productions)


def chomsky_normal_form(grammar):
    gr = grammar.copy()
    # Step 1: remove epilon productions
    gr = removal_epsilon_productions(gr)
    # Step 2: remove cycles
    gr = removal_cycles(gr)
    # Step 3: remove left recursion
    gr, _ = removal_left_recursion(gr)
    # Step 4: remove un
    gr = removal_nonsolitary_terminals(gr)
    # Step 5:
    gr = agrupar_productions_pares(gr)

    return gr


def left_factoring(grammar):
    gr = grammar.copy()

    old_non_terminals = gr.non_terminals
    for token in old_non_terminals:
        old_productions = gr.productions[token].copy()
        times = 1
        for production in old_productions:
            if production in gr.productions[token] and production is not None and len(gr.productions[token]) > 1: # sino esta es que se ha reducido en alguna iteracion anterior
                gr, times = find_prefix(production, gr.productions[token], token, times, "_" + str(times), gr)

    return gr


# cadenas_differents si y solo si la cadena es una producción epsilon o si la cadena y la de referencia no comienzan por
# el mismo token
def different_productions(reference_string, cadena):
    return cadena is None or cadena == [] or reference_string[0] != cadena[0]

#
def find_prefix(reference_string, new_productions, name_prod, times, sufix, grammar):
    gr = grammar.copy()

    prefix_productions = list()
    different = False
    for index, character in enumerate(reference_string):
        for new_production in new_productions:
            # En el momento en el que cadenas que no son differents dejan de coincidir se ha calulado el prefijo común
            if not different_productions(reference_string, new_production) and (len(new_production) < index + 1 or character != new_production[index]):
                different = True
            elif not different_productions(reference_string, new_production) and character == new_production[index] and new_production not in prefix_productions:
                prefix_productions.append(new_production)

        if prefix_productions == []:  # No hay prefijo común
            return gr, times

        if different: # Left factorice
            # Añadimos un token no terminal el cual agrupe todas las productions con sufijo comun
            name = name_prod + sufix
            sufix = "'"
            # Las productions del new token contienen todas las cadenas comunes sin el prefijo
            gr.productions[name] = [prod[index:] for prod in prefix_productions]
            gr.non_terminals.add(name)
            # Sustituimos las productions con prefijo por una que sea el prefijo + new token
            new_productions.append(reference_string[:index] + [name])
            for prefix_prod in prefix_productions:
                new_productions.remove(prefix_prod)

            gr.productions[name_prod] = new_productions
            # Factorizamos a izquierda ahora sobre el new token
            gr, _ = find_prefix(gr.productions[name][0], gr.productions[name], name, 0, sufix, gr)
            return gr, times + 1

    return gr, times


def greibach_normal_form(grammar):
    gr = grammar.copy()

    # Step 1: remove left recursion
    non_terminals, new_productions, nt_tokens = removal_left_recursion(gr)

    # En el orden inverso al elegido para eliminar la recursividad a izquierda eliminamos todas las productions que
    # empiecen por no terminal
    for symbol in reversed(nt_tokens):
        productions_to_remove = []
        for production in gr.productions[symbol]:
            if production is not None and production[0] in gr.non_terminals:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in gr.productions[production[0]]:
                    if production_to_remplace is None:
                        new_productions[symbol].append(production[1:])
                    else:
                        new_productions[symbol].append(production_to_remplace + production[1:])

        for production in productions_to_remove:
            new_productions[symbol].remove(production)

    # Eliminamos todas las productions que empiecen por no terminal de los tokens que se han añadido a la hora de
    # eliminar la recursividad a izquierda
    new_symbols = gr.non_terminals.difference(set(nt_tokens))
    for symbol in new_symbols:
        productions_to_remove = []
        for production in gr.productions[symbol]:
            if production is not None and production[0] in gr.non_terminals:
                productions_to_remove.append(production)
                # Sustituimos en la producción el primer token por todas las productions que tiene
                for production_to_remplace in gr.productions[production[0]]:
                    new_productions[symbol].append(production_to_remplace + production[1:])
        for production in productions_to_remove:
            new_productions[symbol].remove(production)

    return gr
