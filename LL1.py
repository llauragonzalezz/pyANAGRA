import itertools
import re
import conjuntos as conj

def is_ll1(table, terminals, non_terminals):
    num_conflicts = 0
    for token_no_terminal in non_terminals:
        for token_terminal in terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) > 1:
                num_conflicts += 1

    return num_conflicts



def calculate_table(starting_token, terminal_tokens, non_terminal_tokens, productions):
    follow_set = conj.calculate_follow_set(starting_token, terminal_tokens, non_terminal_tokens, productions)
    table = dict()

    for non_terminal_token in non_terminal_tokens:
        for token_terminal in terminal_tokens | {"$"}:
            table[non_terminal_token, token_terminal] = []

    for token in non_terminal_tokens:
        for production in productions[token]:
            first_set_token = set()
            if production is not None:
                epsilon = True
                for t in production:
                    first_set = conj.calculate_first_set_token(t, set(t), terminal_tokens, non_terminal_tokens, productions)
                    first_set_token |= first_set.difference({None})
                    if None not in first_set:
                        epsilon = False
                        break

                if epsilon:
                    first_set_token |= {None}
            else:
                first_set_token = {None}

            for elemento in first_set_token & terminal_tokens:
                #print("table[", token, ",", elemento, "] = ", production)
                table[token, elemento].append(production)

            if None in first_set_token:
                for b in terminal_tokens & follow_set[token]:
                    table[token, b].append(production)
                if "$" in follow_set[token]:
                    table[token, "$"].append(production)

    for non_terminal_token in non_terminal_tokens:
        for token_terminal in terminal_tokens | {"$"}:
            if table[non_terminal_token, token_terminal] == dict():
                table[non_terminal_token, token_terminal] = "error"  # TODO: que pongo
                # error

    return table


def simulate(table, start_token, terminals, input):
    stack = [("$", 0), (start_token, 1)]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    iterador = 2
    it = iter(elementos)
    sig_tok = next(it)
    # simulation table: stack | entry text | output
    simulation_table = []
    simulation_table.append(("", input, ()))

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
            # TODO TRY CATCH POR SI KeyError A LA HORA DE ACCEDER A LA TABLA
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
    # i = 1
    #for entrada in simulation_table:
    #    print(str(i), ") ", entrada)
    #    i += 1

    # snab cuando termine slr, abrir nueva rama, trabajrar con ramas
    return simulation_table
