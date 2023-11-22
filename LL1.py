"""
Filename:
Author: Laura González Pizarro
Description:
"""
import itertools
import re
import conjuntos as conj

def is_ll1(table, gr):
    """
    Calculates if the grammar is LL(1):

    Parameters
    ----------
    table : dict
        A dictionary containing the analysis table of grammar

    terminals : set
        A set containing the terminal symbols of the grammar.

    non_terminals : set
        A set containing the non-terminal symbols of the grammar.

    Returns
    -------
    int
        The number of conflicts in the given grammar. If num_conflicts = 0 the grammar is LL(1)
    """
    num_conflicts = 0
    for token_no_terminal in gr.non_terminals:
        for token_terminal in gr.terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) > 1:
                num_conflicts += 1

    return num_conflicts


def calculate_table(gr):
    """
    Calculates the LL(1) analysis table of a given grammar

    Parameters
    ----------
    gr: Grammar

    Returns
    -------
    dict
        A dictionary containing the LL(1) analysis table of the given grammar.
    """
    follow_set = conj.calculate_follow_set(gr)
    table = dict()

    for non_terminal_token in gr.non_terminals:
        for token_terminal in gr.terminals | {"$"}:
            table[non_terminal_token, token_terminal] = []

    for token in gr.non_terminals:
        for production in gr.productions[token]:
            if production is not None:
                first_set_token = conj.calculate_first_set_sentence(production, gr)
            else:
                first_set_token = {None}

            for elemento in first_set_token & gr.terminals:
                table[token, elemento].append(production)

            if None in first_set_token:
                for b in gr.terminals & follow_set[token]:
                    table[token, b].append(production)
                if "$" in follow_set[token]:
                    table[token, "$"].append(production)

    for non_terminal_token in gr.non_terminals:
        for token_terminal in gr.terminals | {"$"}:
            if table[non_terminal_token, token_terminal] == []:
                table[non_terminal_token, token_terminal] = ["error"]  

    return table


def next_token(sig_tok, it):
    if sig_tok == "'":
        y = next(it)
        if y == "'":
            sig_tok += y
        else:
            sig_tok += y + next(it)
    return sig_tok


def simulate(table, gr, input):
    """
    Calculates the LL(1) parsing table for a given input based on a provided LL(1) grammar.

    Parameters
    ----------
    table : dict
        A dictionary containing the LL(1) analysis table of the grammar.

    gr : Grammar

    input : str
        A string containing the input.

    Returns
    -------
    dict
        A dictionary containing the LL(1) parsing table for a given input based on a provided LL(1) grammar.

    bool
        True if the input is not recognized by the grammar. False otherwise
    """
    stack = [("$", 0), (gr.initial_token, 1)]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    iterador = 2
    it = iter(elementos)
    sig_tok = next(it)
    # simulation table: (stack, entry text, output)
    simulation_table = [("", input, ())]

    sig_tok = next_token(sig_tok, it)

    x = stack[len(stack)-1]
    while x[0] != "$":
        # if x is terminal or x == "$"
        if x[0] in gr.terminals or x[0] == "$":
            # if x == sig_tok
            if x[0] == sig_tok:
                # Copiamos el iterador original
                it_copia, it = itertools.tee(it)
                simulation_table.append((stack.copy(), sig_tok+"".join(it_copia), ()))
                # pop(P)
                stack.pop()
                # sig_tok = yylex()
                sig_tok = next(it)
                sig_tok = next_token(sig_tok, it)

            else: # syntax error
                return [("", input, ()), ("", input, ())], True

        else:
            # if table[s, sig_tok] = X -> Y1 ... Yk
            if table[x[0], sig_tok][0] != "error":
                # trigger production
                it_copia, it = itertools.tee(it) # Copiamos el iterador original
                salida = []
                if table[x[0], sig_tok][0] != None:
                    for token in table[x[0], sig_tok][0]:
                        salida.append((token, iterador))
                        iterador += 1
                else:
                    salida = None

                simulation_table.append((stack.copy(), sig_tok+"".join(it_copia), (x, salida)))
                # pop(P)
                stack.pop()
                if salida is not None:
                    # push(X -> Yk ... Y1)
                    stack.extend(reversed(salida))
            else:
                return [("", input, ()), ("", input, ())], True
        x = stack[len(stack)-1]

    simulation_table.append((stack.copy(), "$", ()))
    # '(' 'x' ';' '(' 'x' ')' ')'
    return simulation_table, False
