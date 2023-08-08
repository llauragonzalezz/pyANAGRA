import itertools
import re


def is_ll1(table, terminals, non_terminals):
    for token_no_terminal in non_terminals:
        for token_terminal in terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) != 1:
                return False
    return True


def simulate(table, start_token, terminals, input):
    print(input)
    stack = ["$", start_token]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    #print("elementos: ", elementos)
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
    #print("sig_tok:", sig_tok)

    x = stack[len(stack)-1]

    while x != "$":
        print()
        print("x:", x)
        if x in terminals or x == "$":
            print("es terminal o simbolo final")
            it_copia, it = itertools.tee(it)
            print("entrada", sig_tok+"".join(it_copia))

            if x == sig_tok:
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
                print("sig_tok:", sig_tok)
            else:
                # errorSintactico
                print("error sintactico")
        else:
            if table[x, sig_tok] != "error":
                # disparamos produccion
                print("disparamos la produccion:", table[x, sig_tok][0])
                it_copia, it = itertools.tee(it)
                print("entrada", sig_tok+"".join(it_copia))

                it_copia, it = itertools.tee(it) # Copiamos el iterador original
                simulation_table.append((stack.copy(), sig_tok+"".join(it_copia), (x, table[x, sig_tok])))
                stack.pop()
                #print(table[x, sig_tok][0])
                if table[x, sig_tok][0] is not None:
                    for token in reversed(table[x, sig_tok][0]):
                        stack.append(token)
                    #print("stack despues de apilar: ", stack)

            else:
                # errorSintactico
                print("error sintactico")
        x = stack[len(stack)-1]

    simulation_table.append((stack.copy(), "$", ()))
    # '(' 'x' ';' '(' 'x' ')' ')'
    for fila in simulation_table:
        print(fila)
    #print(simulation_table)
    return simulation_table
