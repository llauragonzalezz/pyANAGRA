"""
Filename:
Author: Laura González Pizarro
Description:
"""

import itertools
import grammar

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
    """
    aceptado = False
    error = False
    stack = [(0,)]
    elementos = input.strip().split()
    it = iter(elementos)
    n, error_tok = sig_tok(it, action_table)

    index = 0
    simulation_table = [] # simulation table: stack | entry text | output
    simulation_table.append((stack.copy(), input, (), ()))

    while not (aceptado or error or error_tok):
        s = int(stack[len(stack) - 1][0])
        if action_table[s, n][0][:5] == "shift":
            stack.append((n, index))
            stack.append((action_table[s, n][0][6:],))

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), "".join(it_copia), (), (n, index)))
            index += 1

            n, error_tok = sig_tok(it, action_table)

        elif action_table[s, n][0] == "accept":
            aceptado = True
        elif action_table[s, n][0] == "ERROR":
            error = True
        elif action_table[s, n][0][:6] == "reduce":
            production = action_table[s, n][0][7:]
            partes = production.split("→")
            right_part = []
            if partes[1].strip() != "ε":
                for i in range(len(partes[1].strip().split())):
                    stack.pop()
                    right_part.append(stack.pop())

            s = int(stack[len(stack) - 1][0])
            stack.append((partes[0].strip(), index))
            stack.append((go_to_table[s, partes[0].strip()],))
            left_part = (partes[0].strip(), index)

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), n + "".join(it_copia), (left_part, right_part), ()))
            index += 1

    if error_tok or len(simulation_table) == 1:
        return [(stack.copy(), input, (), ()), (stack.copy(), input, (), ())], error or error_tok

    return simulation_table, error or error_tok
