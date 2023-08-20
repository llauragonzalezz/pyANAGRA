import itertools
import re
import conjuntos


def is_slr1(table, terminals, non_terminals):
    num_conflicts = 0
    for token_no_terminal in non_terminals:
        for token_terminal in terminals | {"$"}:
            if len(table[token_no_terminal, token_terminal]) > 1:
                num_conflicts += 1

    return num_conflicts


def extend_grammar(start_token, non_terminal_tokens, productions):
    start_token_extended = start_token + "*"
    productions[start_token_extended] = [['.', start_token]]

    return start_token_extended, {start_token_extended} | non_terminal_tokens, productions


def clausura(I, non_terminal_tokens, productions):
    viejo = []
    nuevo = I
    while viejo != nuevo:
        viejo = nuevo
        for prod in viejo:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.')+1] in non_terminal_tokens:
                for prod_B in productions[prod[prod.index('.')+1]]:
                    if ['.'] + prod_B not in nuevo:
                        nuevo.append(['.'] + prod_B)
    return nuevo


def sucesor(I, token, non_terminal_tokens, productions):
    S = []
    for prod in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == token:
            S.append(prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot+2:])
            if prod.index('.') < len(prod) - 2 and prod[prod.index('.')+2] in non_terminal_tokens:
                for prof_token in productions[prod[prod.index('.') + 2]]:
                    S.append(['.'] + prof_token)

    return clausura(S.copy(), non_terminal_tokens, productions)


def conj_LR0(start_token, non_terminal_tokens, productions):
    old = []
    new = [clausura(productions[start_token], non_terminal_tokens, productions)]
    while old != new:
        old = new
        for I in new:
            prods = {token for prod in I for token in prod if token != '.'}
            for token in prods:
                sucesor_token = sucesor(I, token, non_terminal_tokens, productions)
                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token)

    return new


def action_table(C, start_token, terminal_tokens, non_terminal_tokens, productions):
    action = dict()
    C = [[['.', 'E'], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['E', '.'], ['E', '.', "'+'", 'T']],
         [['T', '.']],
         [["'('", '.', 'E', "')'"], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['id', '.']],
         [['E', "'+'", '.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [["'('", 'E', '.', "')'"], ['E', '.', "'+'", 'T']],
         [['E', "'+'", 'T', '.']],
         [["'('", 'E', "')'", '.']]]
    follow_set = conjuntos.calculate_follow_set(start_token, terminal_tokens, non_terminal_tokens, productions)
    for i in range(len(C)):
        for token_terminal in terminal_tokens:
            for prod in C[i]:
                if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] == token_terminal:
                    sucesor_i_token_terminal = sucesor(C[i], token_terminal, non_terminal_tokens, productions)
                    if sucesor_i_token_terminal in C:
                        action[i, token_terminal] = "desplazar " + str(C.index(sucesor_i_token_terminal))
                if prod.index('.') == len(prod) - 1:
                    action[i, "$"] = "reducir " + "{} → {}".format(token_no_terminal, " ".join(str(x) for x in prod[:-1]))

        for token_no_terminal in non_terminal_tokens.difference({start_token}):
            for prod in C[i]:
                if [x for x in prod if x != '.'] in productions[token_no_terminal] and prod.index('.') == len(prod) - 1:
                    for token_no_terminal_siguiente in follow_set[token_no_terminal]:   # todo no se por que no me van bien las productions a veces:
                        action[i, token_no_terminal_siguiente] = "reducir " + "{} → {}".format(token_no_terminal, " ".join(str(x) for x in prod[:-1]))

        for I in C:
            if [start_token[:-1], '.'] in I:
                action[C.index(I), "$"] = "aceptar"

    for i in range(len(C)):
        for token in terminal_tokens | {"$"}:
            if (i, token) not in action:
                action[i, token] = "ERROR"

    return action


def go_to_table(C, non_terminal_tokens, productions):
    ir_a = dict()
    C = [[['.', 'E'], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['E', '.'], ['E', '.', "'+'", 'T']],
         [['T', '.']],
         [["'('", '.', 'E', "')'"], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['id', '.']],
         [['E', "'+'", '.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [["'('", 'E', '.', "')'"], ['E', '.', "'+'", 'T']],
         [['E', "'+'", 'T', '.']],
         [["'('", 'E', "')'", '.']]]
    #conj_LR0(start_token, non_terminal_tokens, productions)
    for i in range(len(C)):
        for token_no_terminal in non_terminal_tokens:
            sucesor_token = sucesor(C[i], token_no_terminal, non_terminal_tokens, productions)
            if sucesor_token in C:
                ir_a[i, token_no_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in non_terminal_tokens | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"
    return ir_a


def create_automaton(C, terminal_tokens, non_terminal_tokens, productions):
    edges = dict()
    for I in C:
        for token in terminal_tokens | non_terminal_tokens | {"$"}:
            sucesor_token = sucesor(I, token, non_terminal_tokens, productions)
            if sucesor_token in C:
                edges[str(C.index(I)), str(C.index(sucesor_token))] = token

    return edges


def simulate(accion, ir_a, input):
    aceptado = False
    error = False
    stack = [(0,)]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    it = iter(elementos)
    n = next(it)

    index = 0
    # simulation table: stack | entry text | output
    simulation_table = []
    simulation_table.append((stack.copy(), input, (), ()))
    if n == "'":  # if sig_tok is character or string TODO poner tambien si es string "
        y = next(it)
        if y != "'":
            n += y
        else:
            n += y + next(it)
    while not (aceptado or error):
        s = int(stack[len(stack) - 1][0])
        if accion[s, n][:9] == "desplazar":
            stack.append((n, index))
            stack.append((accion[s, n][10:],))

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), "".join(it_copia), (), (n, index)))
            index += 1

            n = next(it)
            if n == "'":  # if sig_tok is character or string TODO poner tambien si es string "
                y = next(it)
                if y != "'":
                    n += y
                else:
                    n += y + next(it)

        elif accion[s, n] == "aceptar":
            aceptado = True
        elif accion[s, n] == "ERROR":
            error = True
        elif accion[s, n][:7] == "reducir":
            production = accion[s, n][8:]
            partes = production.split("→")
            right_part = []
            for i in range(len(partes[1].strip().split())):
                stack.pop()
                right_part.append(stack.pop())

            s = int(stack[len(stack) - 1][0])
            stack.append((partes[0][0], index))
            stack.append((ir_a[s, partes[0][0]],))
            left_part = (partes[0][0], index)
            index += 1

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), n + "".join(it_copia), (left_part, right_part), ()))

    i = 1
    for entrada in simulation_table:
        print(str(i), ") ", entrada)
        i += 1

    return simulation_table
