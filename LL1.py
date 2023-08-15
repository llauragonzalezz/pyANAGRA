import itertools
import re


def is_ll1(table, terminals, non_terminals):
    num_conflicts = 0
    for token_no_terminal in non_terminals:
        for token_terminal in terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) > 1:
                num_conflicts += 1

    return num_conflicts


def simulate(table, start_token, terminals, input):
    stack = [("$", 0), (start_token, 1)]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    #print("elementos: ", elementos)
    iterador = 2
    it = iter(elementos)
    sig_tok = next(it)
    # simulation table: stack | entry text | output
    simulation_table = []
    simulation_table.append(("", input, ()))
    #simulation_table.append((stack, input, (start_token, table[start_token, sig_tok])))

    if sig_tok == "'":
        y = next(it)
        if y == "'":
            sig_tok += y
        else:
            sig_tok += y + next(it)

    x = stack[len(stack)-1]
    while x[0] != "$":
        if x[0] in terminals or x[0] == "$":
            if x[0] == sig_tok:
                # Copiamos el iterador original
                it_copia, it = itertools.tee(it)
                simulation_table.append((stack.copy(), sig_tok+"".join(it_copia), ()))
                stack.pop()
                sig_tok = next(it)

                if sig_tok == "'": # if sig_tok is character or string TODO poner tambien si es string "
                    y = next(it)
                    if y != "'":
                        sig_tok += y
                    else:
                        sig_tok += y + next(it)
            else:
                # errorSintactico
                print("error sintactico")
        else:
            if table[x[0], sig_tok] != "error":
                # disparamos produccion
                it_copia, it = itertools.tee(it) # Copiamos el iterador original
                salida = []
                if table[x[0], sig_tok][0] is not None:
                    for token in table[x[0], sig_tok][0]:
                        salida.append((token, iterador))
                        iterador += 1
                else:
                    salida = None

                simulation_table.append((stack.copy(), sig_tok+"".join(it_copia), (x, salida)))
                stack.pop()
                if salida is not None:
                    stack.extend(reversed(salida))
            else:
                # errorSintactico
                print("error sintactico")
        x = stack[len(stack)-1]

    simulation_table.append((stack.copy(), "$", ()))
    # '(' 'x' ';' '(' 'x' ')' ')'

    return simulation_table
