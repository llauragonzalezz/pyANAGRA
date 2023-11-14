"""
Filename:
Author: Laura González Pizarro
Description:
"""
import itertools
import conjuntos


def is_slr1(table):
    num_conflicts = 0
    for keys in table:
        if len(table[keys]) > 1:
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
        for token, prod in viejo:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.')+1] in non_terminal_tokens:
                for prod_B in productions[prod[prod.index('.')+1]]:
                    if prod_B is None and (prod[prod.index('.')+1], ['.']) not in nuevo:
                        nuevo.append((prod[prod.index('.')+1], ['.']))
                    elif prod_B is not None and (prod[prod.index('.')+1], ['.'] + prod_B) not in nuevo:
                        nuevo.append((prod[prod.index('.')+1], ['.'] + prod_B))

    return nuevo


def sucesor(I, token, non_terminal_tokens, productions):
    S = []
    for token_prod, prod in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == token:
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot+2:]))

    return clausura(S.copy(), non_terminal_tokens, productions)


def conj_LR0(start_token, non_terminal_tokens, productions):
    old = []
    new = [clausura([(start_token, prod) for prod in productions[start_token]], non_terminal_tokens, productions)]
    while old != new:
        old = new.copy()
        for I in new:
            prods = {token for _, prod in I for token in prod if token != '.'}
            for token in prods:
                sucesor_token = sucesor(I, token, non_terminal_tokens, productions)
                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token)

    return new


def action_table(C, start_token, terminal_tokens, non_terminal_tokens, productions, follow_set):
    action = dict()
    #follow_set = conjuntos.calculate_follow_set(start_token[:-1], terminal_tokens, non_terminal_tokens, productions)

    for i in range(len(C)):
        for token, prod in C[i]:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] in terminal_tokens:
                terminal_token = prod[prod.index('.') + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_token, non_terminal_tokens, productions)
                if sucesor_i_token_terminal in C:
                    new_action = "desplazar " + str(C.index(sucesor_i_token_terminal))
                    if (i, terminal_token) in action and new_action not in action[i, terminal_token]:
                        action[i, terminal_token].append(new_action)
                    elif (i, terminal_token) not in action:
                        action[i, terminal_token] = [new_action]

            if prod.index('.') == len(prod) - 1:
                if prod[0] == '.':   # epsilon production
                    new_action = "reducir " + token + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))

                if (i, "$") in action and new_action not in action[i, "$"]:
                    action[i, "$"].append(new_action)
                elif (i, "$") not in action:
                    action[i, "$"] = [new_action]

        for token, prod in C[i]:
            if token != start_token and prod.index('.') == len(prod) - 1:
                for token_no_terminal_siguiente in follow_set[token]:
                    if prod[0] == '.':  # epsilon production
                        new_action = "reducir " + token + "  → ε"
                    else:
                        new_action = "reducir " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))

                    if (i, token_no_terminal_siguiente) in action and new_action not in action[i, token_no_terminal_siguiente]:
                        action[i, token_no_terminal_siguiente].append(new_action)
                    elif (i, token_no_terminal_siguiente) not in action:
                        action[i, token_no_terminal_siguiente] = [new_action]

        for I in C:
            if (start_token, [start_token[:-1], '.']) in I:
                action[C.index(I), "$"] = ["aceptar"]

    for i in range(len(C)):
        for token in terminal_tokens | {"$"}:
            if (i, token) not in action:
                action[i, token] = ["ERROR"]

    return action


def go_to_table(C, non_terminal_tokens, productions):
    ir_a = dict()
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


def sig_tok(it, accion):
    n = next(it)
    return n, not any(n == key[1] for key in accion.keys())


def simulate(accion, ir_a, input):
    aceptado = False
    error = False
    stack = [(0,)]
    elementos = input.strip().split()
    it = iter(elementos)
    n, error_tok = sig_tok(it, accion)

    index = 0
    simulation_table = [] # simulation table: stack | entry text | output
    simulation_table.append((stack.copy(), input, (), ()))

    while not (aceptado or error or error_tok):
        s = int(stack[len(stack) - 1][0])
        if accion[s, n][0][:9] == "desplazar":
            stack.append((n, index))
            stack.append((accion[s, n][0][10:],))

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), "".join(it_copia), (), (n, index)))
            index += 1

            n, error_tok = sig_tok(it, accion)

        elif accion[s, n][0] == "aceptar":
            aceptado = True
        elif accion[s, n][0] == "ERROR":
            error = True
        elif accion[s, n][0][:7] == "reducir":
            production = accion[s, n][0][8:]
            partes = production.split("→")
            right_part = []
            if partes[1].strip() != "ε":
                for i in range(len(partes[1].strip().split())):
                    stack.pop()
                    right_part.append(stack.pop())

            s = int(stack[len(stack) - 1][0])
            stack.append((partes[0].strip(), index))
            stack.append((ir_a[s, partes[0].strip()],))
            left_part = (partes[0].strip(), index)

            it_copia, it = itertools.tee(it)
            simulation_table.append((stack.copy(), n + "".join(it_copia), (left_part, right_part), ()))
            index += 1

    if error_tok or len(simulation_table) == 1:
        return [(stack.copy(), input, (), ()), (stack.copy(), input, (), ())], error or error_tok

    return simulation_table, error or error_tok
