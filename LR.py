"""
Filename:
Author: Laura González Pizarro
Description:
"""
import conjuntos as conj
import grammar


def is_lr(table):
    num_conflicts = 0
    for keys in table:
        if len(table[keys]) > 1:
            num_conflicts += 1

    return num_conflicts


def extend_grammar(gr):
    gr.initial_token_extended = gr.initial_token + "*"
    gr.productions[gr.initial_token_extended] = [['.', gr.initial_token]]

    return grammar.Grammar(gr.initial_token_extended, gr.terminals, {gr.initial_token_extended} | gr.non_terminals, gr.productions)


def clausura(I, first_set, gr):
    nuevo = I
    bool_new = True
    while bool_new:  # poner booleano
        bool_new = False
        for token, prod, terminal in nuevo:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in gr.non_terminals: # A -> α.Bþ, {terminal}
                for prod_B in gr.productions[prod[pos_dot + 1]]: # B -> y
                    first_set_token = set()
                    if pos_dot < len(prod) - 2:  # Pri(þ)
                        first_set_token = conj.calculate_first_set_sentence_fs(prod[pos_dot + 2:], first_set)
                    if pos_dot >= len(prod) - 2:  # Si no existe þ => Pri(a)
                        first_set_token = terminal
                    for b in gr.terminals & first_set_token:
                        if prod_B is None and (prod[pos_dot + 1], ['.'], {b}) not in nuevo:
                            nuevo.append((prod[pos_dot + 1], ['.'], {b}))
                            bool_new = True
                        elif prod_B is not None and (prod[pos_dot + 1], ['.'] + prod_B, {b}) not in nuevo:
                            nuevo.append((prod[pos_dot + 1], ['.'] + prod_B, {b}))
                            bool_new = True

    # agrupamos
    nuevas_tuplas = []
    for token, prod, terminal in nuevo:
        encontrado = False
        for i, tupla in enumerate(nuevas_tuplas):
            if tupla[0] == token and tupla[1] == prod:
                nuevas_tuplas[i] = (tupla[0], tupla[1], tupla[2] | terminal)
                encontrado = True
        if not encontrado:
            nuevas_tuplas.append((token, prod, terminal))

    return nuevas_tuplas

def sucesor(I, token, first_set, gr):
    S = []
    for token_prod, prod, terminal in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == token:
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot + 2:], terminal))

    return clausura(S, first_set, gr)

def conj_LR1(first_set, gr):
    new = [clausura([(gr.initial_token, prod, {'$'}) for prod in gr.productions[gr.initial_token]], first_set, gr)]
    diccionario = dict()
    bool_new = True
    while bool_new:
        bool_new = False
        for I in new:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            for token in prods:
                if (str(I), token) not in diccionario:
                    diccionario[str(I), token] = sucesor(I, token, first_set, gr)
                sucesor_token = diccionario[str(I), token]

                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token)
                    bool_new = True

    return new


def action_table(first_set, C, gr):
    """
    Calculates the "action" table of a given rightmost LALR grammar.

    Parameters
    ----------
    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    C: list
        A list containing the canonical collection of LR(0) configurations.

    gr : Grammar

    Returns
    -------
    dict
        A dictionary containing the "action" table of the given grammar.
    """
    action = dict()

    for i in range(len(C)):
        for symbol, prod, terminal in C[i]:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in gr.terminals:
                terminal_token = prod[pos_dot + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_token, first_set, gr)
                if sucesor_i_token_terminal in C:
                    new_action = "desplazar " + str(C.index(sucesor_i_token_terminal))
                    if (i, terminal_token) in action and new_action not in action[i, terminal_token]:
                        action[i, terminal_token].append(new_action)
                    elif (i, terminal_token) not in action:
                        action[i, terminal_token] = [new_action]

            if pos_dot == len(prod) - 1:
                if prod[0] == '.':   # epsilon production
                    new_action = "reducir " + symbol + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(symbol, " ".join(str(x) for x in prod[:-1]))

                if (i, "$") in action and new_action not in action[i, "$"]:
                        action[i, "$"].append(new_action)
                elif (i, "$") not in action:
                    action[i, "$"] = [new_action]

        for symbol, prod, terminal in C[i]:
            if symbol != gr.initial_token and pos_dot == len(prod) - 1:
                if prod[0] == '.':  # epsilon production
                    new_action = "reducir " + symbol + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(symbol, " ".join(str(x) for x in prod[:-1]))

                for t in terminal:
                    if (i, t) in action and new_action not in action[i, t]:
                        action[i, t].append(new_action)
                    elif (i, t) not in action:
                        action[i, t] = [new_action]
            elif symbol == gr.initial_token and pos_dot == len(prod) - 1:
                action[i, "$"] = ["aceptar"]

    for i in range(len(C)):
        for symbol in gr.terminals:
            if (i, symbol) not in action:
                action[i, symbol] = ["ERROR"]

    return action


def go_to_table(first_set, C, gr):
    """
    Calculates the "go to" table of a given LR grammar.

    Parameters
    ----------
    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    C: list
        A list containing the canonical collection of LR(0) configurations.

    gr : Grammar

    Returns
    -------
    dict
        A dictionary containing the "go to" table of the given grammar.
    """
    ir_a = dict()
    #conj_LR0(gr.initial_token, gr.non_terminals, productions)
    for i in range(len(C)):
        for non_terminal in gr.non_terminals:
            sucesor_token = sucesor(C[i], non_terminal, first_set, gr)
            if sucesor_token in C:
                ir_a[i, non_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in gr.non_terminals | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"

    return ir_a


def create_automaton(first_set, C, gr):
    """
    Calculates the automaton of a given LR grammar.

    Parameters
    ----------
    first_set: dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    C : list
    
    gr : Grammar

    Returns
    -------
    dict
        A dictionary containing the automaton of the given grammar.

    """
    edges = dict()
    for I in C:
        for symbol in gr.terminals | gr.non_terminals:
            sucesor_token = sucesor(I, symbol, first_set, gr)
            if sucesor_token in C:
                edges[str(C.index(I)), str(C.index(sucesor_token))] = symbol

    return edges
