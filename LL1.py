import itertools
import re


def is_ll1(table, terminals, non_terminals):
    for token_no_terminal in non_terminals:
        for token_terminal in terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) != 1:
                return False
    return True


def simulate(table, start_token, terminals, input):

    stack = ["$", start_token]
    simulation_table = []

    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    print("elementos: ", elementos)
    it = iter(elementos)
    sig_tok = next(it)
    if sig_tok == "'":
        y = next(it)
        if y == "'":
            sig_tok += y
        else:
            sig_tok += y + next(it)
    print("sig_tok:", sig_tok)

    x = stack[len(stack)-1]

    while x != "$":
        print("x:", x)
        if x in terminals or x == "$":
            if x == sig_tok:
                # Copiamos el iterador original
                it_copia, it = itertools.tee(it)
                simulation_table.append((stack.copy(), "".join(it_copia), ()))
                stack.pop()

                sig_tok = next(it)
                if sig_tok == "'":
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
                it_copia, it = itertools.tee(it) # Copiamos el iterador original
                simulation_table.append((stack.copy(), "".join(it_copia), (x, table[x, sig_tok])))

                stack.pop()

                print(table[x, sig_tok][0])
                if table[x, sig_tok][0] is not None:
                    for token in reversed(table[x, sig_tok][0]):
                        stack.append(token)
                    print("stack despues de apilar: ", stack)



            else:
                # errorSintactico
                print("error sintactico")
        x = stack[len(stack)-1]

    return simulation_table
