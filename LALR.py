"""
Filename:
Author: Laura González Pizarro
Description:
"""
import LR

def conj_LR1(first_set, gr):
    """
    Calculates the 'follow' set of all tokens in the context of a grammar.

    Parameters
    ----------
    first_set : dict
        A dictionary containing the 'first' set of all symbols of the grammar.

    gr : Grammar

    Returns
    -------
    dict
        A dictionary containing the 'follow' set of all symbols of the grammar.
    """
    old = []
    new = [LR.clausura([(gr.initial_token, prod, {'$'}) for prod in gr.productions[gr.initial_token]], first_set, gr)]
    diccionario = dict()
    while old != new:
        old = new
        for I in new:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            # for each X ∈ N ∪ T
            for token in prods:
                # Calculate suc(I,X)
                if (str(I), token) not in diccionario:
                    diccionario[str(I), token] = LR.sucesor(I, token, first_set, gr)
                sucesor_token = diccionario[str(I), token]

                # if suc(I,X) != ∅ and suc(I,X) ∉ C
                if sucesor_token != [] and sucesor_token not in new:
                    aniadir = True
                    # if suc(C[i], b) <= C[j]
                    for i, c in enumerate(new):
                        if len(c) == len(sucesor_token):
                            for j in range(len(sucesor_token)):
                                if c[j][0] != sucesor_token[j][0] or c[j][1] != sucesor_token[j][1]:
                                    break
                            else:
                                aniadir = False
                                break

                    if aniadir:
                        # C = C ∪ suc(I,X)
                        new.append(sucesor_token)
                    else:
                        new[i] = []
                        # suc(C[i], b) <= C[j]  => merge
                        for j in range(len(sucesor_token)):
                            if c[j][2] - sucesor_token[j][2] == c[j][2]:
                                new[i].append((c[j][0], c[j][1], c[j][2] | sucesor_token[j][2]))
                            else:
                                new[i].append((c[j][0], c[j][1], c[j][2]))

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

    gr: Grammar

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
                sucesor_i_token_terminal = LR.sucesor(C[i], terminal_token, first_set, gr)
                aniadir = False
                # if suc(C[i], b) <= C[j]
                for j, c in enumerate(C):
                    if len(c) == len(sucesor_i_token_terminal):
                        for k in range(len(sucesor_i_token_terminal)):
                            if c[k][0] != sucesor_i_token_terminal[k][0] or c[k][1] != sucesor_i_token_terminal[k][1]:
                                break
                        else:
                            aniadir = True
                            break

                if aniadir:
                    new_action = "shift " + str(j)
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
    Calculates the "go to" table of a given rightmost LALR grammar.

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
    for i in range(len(C)):
        for non_terminal in gr.non_terminals:
            sucesor_token = LR.sucesor(C[i], non_terminal, first_set, gr)
            add = False
            # if suc(C[i], non_terminal) <= C[j]
            for j, c in enumerate(C):
                if len(c) == len(sucesor_token):
                    for k in range(len(sucesor_token)):
                        if c[k][0] != sucesor_token[k][0] or c[k][1] != sucesor_token[k][1]:
                            break
                    else:
                        add = True
                        break

            if add:
                go_to[i, non_terminal] = j

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
            sucesor_token = LR.sucesor(I, symbol, first_set, gr)
            aniadir = False
            # if suc(C[i], non_terminal) <= C[j]
            for i, c in enumerate(C):
                if len(c) == len(sucesor_token):
                    for j in range(len(sucesor_token)):
                        if c[j][0] != sucesor_token[j][0] or c[j][1] != sucesor_token[j][1]:
                            break
                    else:
                        aniadir = True
                        break

            if aniadir:
                # edges[index(I), i] = symbol
                edges[str(C.index(I)), str(i)] = symbol
    return edges
