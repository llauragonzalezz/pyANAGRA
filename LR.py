"""
Filename:
Author: Laura González Pizarro
Description:
"""
import conjuntos as conj
import grammar


def is_lr(action_table):
    num_conflicts = 0
    for keys in action_table:
        if len(action_table[keys]) > 1:
            num_conflicts += 1

    return num_conflicts


def clausura(I, first_set, gr):
    """
    Calculates the LR(0) clausure of the grammar.

    Parameters
    ----------
    I: list
         A list containing the configurations for an expanded grammar.

    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    gr : Grammar

    Returns
    -------
    list
        A list containing LR(0) clausure of the grammar.
    """
    nuevo = I
    bool_new = True
    while bool_new:  # poner booleano
        bool_new = False
        # for each "A -> α . B þ, a "
        for symbol, prod, terminal in nuevo:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in gr.non_terminals: # A -> α.Bþ, {terminal}
                # for each B -> y
                for prod_B in gr.productions[prod[pos_dot + 1]]:
                    first_set_token = set()
                    if pos_dot < len(prod) - 2:  # PRI(þ)
                        first_set_token = conj.calculate_first_set_sentence_fs(prod[pos_dot + 2:], first_set)
                    else:  # if þ does not exist => PRI(þa) = Pri(a)
                        first_set_token = terminal
                    # for each b ∈ T PRI(þa)
                    for b in gr.terminals & first_set_token:
                        # if "B -> . y, b" ∉ I*
                        if prod_B is None and (prod[pos_dot + 1], ['.'], {b}) not in nuevo: # epsilon production
                            # I* = I* ∪ {B → .γ, b}
                            nuevo.append((prod[pos_dot + 1], ['.'], {b}))
                            bool_new = True
                        elif prod_B is not None and (prod[pos_dot + 1], ['.'] + prod_B, {b}) not in nuevo:
                            # I* = I* ∪ {B → .γ, b}
                            nuevo.append((prod[pos_dot + 1], ['.'] + prod_B, {b}))
                            bool_new = True

    # group
    new_tuples = []
    for symbol, prod, terminal in nuevo:
        encontrado = False
        for i, tuple in enumerate(new_tuples):
            if tuple[0] == symbol and tuple[1] == prod:
                new_tuples[i] = (tuple[0], tuple[1], tuple[2] | terminal)
                encontrado = True
        if not encontrado:
            new_tuples.append((symbol, prod, terminal))

    return new_tuples


def sucesor(I, symbol, first_set, gr):
    """
    Calculates the successors of I with respect to the symbol X.

    Parameters
    ----------
    I: list
         A list containing the configurations for an expanded grammar.

    symbol: str
        The symbol on which the successor set is calculated.

    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    gr : Grammar

    Returns
    -------
    list
        A list containing the successors of I with respect to the symbol X.
    """
    S = []
    # for each A → α. X ß ∈ I*
    for token_prod, prod, terminal in I:
        pos_dot = prod.index('.')
        # X == symbol
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == symbol:
            # S = S ∪ {A → α X. ß}
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot + 2:], terminal))

    return clausura(S, first_set, gr)

def conj_LR1(first_set, gr):
    """
    Calculates the "action" table of a given rightmost LALR grammar.

    Parameters
    ----------
    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    gr : Grammar

    Returns
    -------
    dict
        A dictionary containing the "action" table of the given grammar.
    """
    # C = {clausura(S* → S)}
    C = [clausura([(gr.initial_token, prod, {'$'}) for prod in gr.productions[gr.initial_token]], first_set, gr)]
    diccionario = dict()
    bool_new = True
    while bool_new:
        bool_new = False
        for I in C:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            # for each X ∈ N ∪ T
            for token in prods:
                # Calculate suc(I,X)
                if (str(I), token) not in diccionario:
                    diccionario[str(I), token] = sucesor(I, token, first_set, gr)
                sucesor_token = diccionario[str(I), token]

                # if suc(I,X) != ∅ and suc(I,X) ∉ C
                if sucesor_token != [] and sucesor_token not in C:
                    # C = C ∪ suc(I,X)
                    C.append(sucesor_token)
                    bool_new = True

    return C


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
            # if " A -> α . a β, a" ∈ C[i]
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in gr.terminals:
                terminal_token = prod[pos_dot + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_token, first_set, gr)

                # if suc(C[i], b) = C[j]
                if sucesor_i_token_terminal in C:
                    new_action = "shift " + str(C.index(sucesor_i_token_terminal))
                    # action[i, a] = "shift j "
                    if (i, terminal_token) in action and new_action not in action[i, terminal_token]:
                        action[i, terminal_token].append(new_action)
                    elif (i, terminal_token) not in action:
                        action[i, terminal_token] = [new_action]

            # if "A -> . α, a" and A != initial_token
            if symbol != gr.initial_token and pos_dot == len(prod) - 1:
                if prod[0] == '.':  # epsilon production
                    new_action = "reduce " + symbol + "  → ε"
                else:
                    new_action = "reduce " + "{} → {}".format(symbol, " ".join(str(x) for x in prod[:-1]))

                for t in terminal:
                    # action[i, a] = "reduce A ->  α "
                    if (i, t) in action and new_action not in action[i, t]:
                        action[i, t].append(new_action)
                    elif (i, t) not in action:
                        action[i, t] = [new_action]
            # if S* -> S . ∈ C[i]
            elif symbol == gr.initial_token and pos_dot == len(prod) - 1:
                # action[i, $] = "accept"
                action[i, "$"] = ["accept"]

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
    go_to = dict()
    #conj_LR0(gr.initial_token, gr.non_terminals, productions)
    for i in range(len(C)):
        for non_terminal in gr.non_terminals:
            sucesor_token = sucesor(C[i], non_terminal, first_set, gr)
            # if suc(C[i], non_terminal) == C[j]
            if sucesor_token in C:
                # go_to[i, non_terminal] = j
                go_to[i, non_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in gr.non_terminals | {"$"}:
            if (i, token) not in go_to:
                go_to[i, token] = "ERROR"

    return go_to


def create_automaton(first_set, C, gr):
    """
    Calculates the automaton of a given LR grammar.

    Parameters
    ----------
    first_set: dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    C : list
        A list containing the canonical collection of LR(0) configurations.

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
            # if suc(C[i], symbol) ∈ C
            if sucesor_token in C:
                # edges[index(I), i] = symbol
                edges[str(C.index(I)), str(C.index(sucesor_token))] = symbol

    return edges
