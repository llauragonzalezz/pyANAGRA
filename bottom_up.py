"""
Filename:
Author: Laura González Pizarro
Description:
"""

import itertools
import grammar


def is_bottom_up(action_table):
    """
    Check if the given grammar is  a bottom-up grammar.

    Parameters
    ----------
    action_table : dict
        A dictionary representing the action table for the grammar.

    Returns
    -------
    bool
        True if the grammar is a bottom-up grammar, False otherwise.
    """
    num_conflicts = 0
    for keys in action_table:
        # conflict found
        if len(action_table[keys]) > 1:
            num_conflicts += 1

    return num_conflicts


def extend_grammar(gr):
    initial_token_extended = gr.initial_token + "*"
    gr.productions[initial_token_extended] = [['.', gr.initial_token]]
    return grammar.Grammar(initial_token_extended, gr.terminals, {initial_token_extended} | gr.non_terminals, gr.productions)


def sig_tok(it, accion):
    n = next(it)
    return n, not any(n == key[1] for key in accion.keys())


def simulate(action_table, go_to_table, input):
    """
    Calculates the parsing table for a given input based on a provided rightmost grammar(SLR, LALR, LR).

    Parameters
    ----------
    action_table : dict
        A dictionary containing the "action" table of the grammar.

    go_to_table : dict
        A dictionary containing the "go to" analysis table of the grammar.

    input : str
        A string containing the input.

    Returns
    -------
    dict
        A dictionary containing the parsing table for a given input based on a provided grammar.

    bool
        True if the input is not recognized by the grammar. False otherwise
    """
    accept = False
    error = False
    stack = [(0,)]  # P = stack
    elements = input.strip().split()
    it = iter(elements)

    n, error_tok = sig_tok(it, action_table)

    index = 0
    # simulation table: (stack, entry text, output)
    simulation_table = [(stack.copy(), input, (), ())]

    while not (accept or error or error_tok):
        # s = top(P)
        s = int(stack[len(stack) - 1][0])
        # if action[s,n] = "shift A -> þ"
        if action_table[s, n][0][:5] == "shift":
            # push(P, n)
            stack.append((n, index))
            # push (P, s')
            stack.append((action_table[s, n][0][6:],))

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), " ".join(it_copia), (), (n, index)))
            index += 1

            n, error_tok = sig_tok(it, action_table)
        # action[s, n] = "accept"
        elif action_table[s, n][0] == "accept":
            print(stack)
            simulation_table.append(([], "$", (), ()))
            accept = True
        # action[s, n] = "ERROR"
        elif action_table[s, n][0] == "ERROR":
            error = True
        # action[s, n] = "reduce A -> þ"
        elif action_table[s, n][0][:6] == "reduce":
            production = action_table[s, n][0][7:]
            partes = production.split("→")
            right_part = []
            if partes[1].strip() != "ε":
                # for i = 1 ... þ
                for i in range(len(partes[1].strip().split())):
                    stack.pop()  # pop(P)
                    right_part.append(stack.pop())  # pop(P)

            # s = top(P)
            s = int(stack[len(stack) - 1][0])
            # push(P, A)
            stack.append((partes[0].strip(), index))
            # push(P, go_to[s, A])
            stack.append((go_to_table[s, partes[0].strip()],))
            left_part = (partes[0].strip(), index)

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), n + " ".join(it_copia), (left_part, right_part), ()))
            index += 1

    if error_tok or error or len(simulation_table) == 1:
        return [(stack.copy(), input, (), ()), (stack.copy(), input, (), ())], error or error_tok

    return simulation_table, error or error_tok
