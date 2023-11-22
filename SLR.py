"""
Filename:
Author: Laura González Pizarro
Description:
"""

def is_slr1(table):
    num_conflicts = 0
    for keys in table:
        if len(table[keys]) > 1:
            num_conflicts += 1

    return num_conflicts


def clausura(I, gr):
    """
    Calculates the LR(0) clausure of the grammar.

    Parameters
    ----------
    I: list
         A list containing the configurations for an expanded grammar.

    gr : Grammar

    Returns
    -------
    list
        A list containing LR(0) clausure of the grammar.
    """
    old = []
    new = I

    while old != new:
        old = new
        # for each A → α. B ß ∈ I*
        for symbol, prod in old:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.')+1] in gr.non_terminals:
                # for each B → γ in productions
                for prod_B in gr.productions[prod[prod.index('.')+1]]:
                    # if B → .γ ∉ I*
                    if prod_B is None and (prod[prod.index('.')+1], ['.']) not in new:
                        # I* = I* ∪ {B → .γ}
                        new.append((prod[prod.index('.')+1], ['.']))
                    elif prod_B is not None and (prod[prod.index('.')+1], ['.'] + prod_B) not in new: # case eps prod
                        # I* = I* ∪ {B → .γ}
                        new.append((prod[prod.index('.')+1], ['.'] + prod_B))

    return new


def sucesor(I, symbol, gr):
    """
    Calculates the successors of I with respect to the symbol X.

    Parameters
    ----------
    I: list
         A list containing the configurations for an expanded grammar.

    symbol: str
        The symbol on which the successor set is calculated.

    gr : Grammar

    Returns
    -------
    list
        A list containing the successors of I with respect to the symbol X.
    """
    S = []
    for token_prod, prod in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == symbol:
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot+2:]))

    return clausura(S.copy(), gr)


def conj_LR0(gr):
    old = []
    new = [clausura([(gr.initial_token, prod) for prod in gr.productions[gr.initial_token]], gr)]
    while old != new:
        old = new.copy()
        for I in new:
            prods = {token for _, prod in I for token in prod if token != '.'}
            for token in prods:
                sucesor_token = sucesor(I, token, gr)
                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token)

    return new


def action_table(C, gr, follow_set):
    """
    Calculates the "action" table of a given rightmost SLR grammar.

    Parameters
    ----------
    C: list
        A list containing the canonical collection of LR(0) configurations.

    gr : Grammar

    follow_set : dict
        A dictionary containing the 'follow' set of all symbols of the grammar.

    Returns
    -------
    dict
        A dictionary containing the "action" table of the given grammar.
    """
    action = dict()

    for i in range(len(C)):
        for token, prod in C[i]:
            # if A -> α . a β
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] in gr.terminals:
                terminal_symbol = prod[prod.index('.') + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_symbol, gr)
                # If suc(C[i], a) = C[j]
                if sucesor_i_token_terminal in C:
                    new_action = "shift " + str(C.index(sucesor_i_token_terminal))
                    # action[i, a] = "shift j "
                    if (i, terminal_symbol) in action and new_action not in action[i, terminal_symbol]:
                        action[i, terminal_symbol].append(new_action)
                    elif (i, terminal_symbol) not in action:
                        action[i, terminal_symbol] = [new_action]

            # if A -> . α and A != initial_token
            if token != gr.initial_token and prod.index('.') == len(prod) - 1:
                # for each a in SIG(A)
                for token_no_terminal_siguiente in follow_set[token]:
                    if prod[0] == '.':  # epsilon production
                        new_action = "reduce " + token + "  → ε"
                    else:
                        new_action = "reduce " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))
                    # action[i, a] = "reduce A ->  α "
                    if (i, token_no_terminal_siguiente) in action and new_action not in action[i, token_no_terminal_siguiente]:
                        action[i, token_no_terminal_siguiente].append(new_action)
                    elif (i, token_no_terminal_siguiente) not in action:
                        action[i, token_no_terminal_siguiente] = [new_action]

        for I in C:
            # if S* -> S . ∈ C[i]
            if (gr.initial_token, [gr.initial_token[:-1], '.']) in I:
                # action[i, $] = "accept"
                action[C.index(I), "$"] = ["accept"]

    for i in range(len(C)):
        for token in gr.terminals | {"$"}:
            if (i, token) not in action:
                action[i, token] = ["ERROR"]

    return action


def go_to_table(C, gr):
    """
    Calculates the "go to" table of a given rightmost SLR grammar.

    Parameters
    ----------
    C: list
        A list containing the canonical collection of LR(0) configurations.

    gr.non_terminals : set
        A set containing non-terminal symbols.

    gr.productions : dict
        A dictionary representing the gr.productions of the grammar.

    Returns
    -------
    dict
        A dictionary containing the "go to" table of the given grammar.
    """

    ir_a = dict()
    for i in range(len(C)):
        for token_no_terminal in gr.non_terminals:
            sucesor_token = sucesor(C[i], token_no_terminal, gr)
            if sucesor_token in C:
                ir_a[i, token_no_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in gr.non_terminals | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"

    return ir_a


def create_automaton(C, gr):
    """
    Calculates the automaton of a given LR grammar.

    Parameters
    ----------

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
        for token in gr.terminals | gr.non_terminals | {"$"}:
            sucesor_token = sucesor(I, token, gr)
            # if suc(C[i], symbol) ∈ C
            if sucesor_token in C:
                # edges[index(I), i] = symbol
                edges[str(C.index(I)), str(C.index(sucesor_token))] = token

    return edges

