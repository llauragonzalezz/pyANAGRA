import conjuntos as conj
import operacionesTransformacion as op

def is_lr(table):
    num_conflicts = 0
    for keys in table:
        if len(table[keys]) > 1:
            num_conflicts += 1

    return num_conflicts


def extend_grammar(start_token, non_terminal_tokens, productions):
    start_token_extended = start_token + "*"
    productions[start_token_extended] = [['.', start_token]]

    return start_token_extended, {start_token_extended} | non_terminal_tokens, productions

def clausura(I, first_set, terminal_tokens, non_terminal_tokens, productions):
    nuevo = I
    bool_new = True
    while bool_new:  # poner booleano
        bool_new = False
        for token, prod, terminal in nuevo:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in non_terminal_tokens: # A -> α.Bþ, {terminal}
                for prod_B in productions[prod[pos_dot + 1]]: # B -> y
                    first_set_token = set()
                    if pos_dot < len(prod) - 2:  # Pri(þ)
                        first_set_token = conj.calculate_first_set_sentence_fs(prod[pos_dot + 2:], first_set, terminal_tokens, non_terminal_tokens, productions)
                    if pos_dot >= len(prod) - 2:  # Si no existe þ => Pri(a)
                        first_set_token = terminal
                    for b in terminal_tokens & first_set_token:
                        if prod_B is None and (prod[pos_dot + 1], ['.'], {b}) not in nuevo:
                            nuevo.append((prod[pos_dot + 1], ['.'], {b}))
                            bool_new = True
                        elif prod_B is not None and (prod[pos_dot + 1], ['.'] + prod_B, {b}) not in nuevo:
                            nuevo.append((prod[pos_dot + 1], ['.'] + prod_B, {b}))
                            bool_new = True

    # agrupamos
    nuevas_tuplas = []
    for token, prod, terminal in nuevo:
        encontrado = False
        for i, tupla in enumerate(nuevas_tuplas):
            if tupla[0] == token and tupla[1] == prod:
                nuevas_tuplas[i] = (tupla[0], tupla[1], tupla[2] | terminal)
                encontrado = True
        if not encontrado:
            nuevas_tuplas.append((token, prod, terminal))

    return nuevas_tuplas

def sucesor(I, token, first_set, terminal_tokens, non_terminal_tokens, productions):
    S = []
    for token_prod, prod, terminal in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == token:
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot + 2:], terminal))

    return clausura(S, first_set, terminal_tokens, non_terminal_tokens, productions)

def conj_LR1(first_set, start_token, terminal_tokens, non_terminal_tokens, productions):
    new = [clausura([(start_token, prod, {'$'}) for prod in productions[start_token]], first_set, terminal_tokens, non_terminal_tokens, productions)]
    conjunto_I = []
    diccionario = dict()
    bool_new = True
    while bool_new:
        bool_new = False
        for I in new:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            for token in prods:
                if (I, token) not in conjunto_I:
                    conjunto_I.append((I, token))
                    diccionario[len(conjunto_I)-1, token] = sucesor(I, token, first_set, terminal_tokens, non_terminal_tokens, productions)
                    sucesor_token = diccionario[len(conjunto_I)-1, token]
                else:
                    sucesor_token = diccionario[conjunto_I.index((I, token)), token]

                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token)
                    bool_new = True

    return new

def action_table(first_set, C, start_token, terminal_tokens, non_terminal_tokens, productions):
    action = dict()

    for i in range(len(C)):
        for token, prod, terminal in C[i]:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in terminal_tokens:
                terminal_token = prod[pos_dot + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_token, first_set, terminal_tokens, non_terminal_tokens, productions)
                if sucesor_i_token_terminal in C:
                    new_action = "desplazar " + str(C.index(sucesor_i_token_terminal))
                    if (i, terminal_token) in action and new_action not in action[i, terminal_token]:
                        action[i, terminal_token].append(new_action)
                    elif (i, terminal_token) not in action:
                        action[i, terminal_token] = [new_action]

            if pos_dot == len(prod) - 1:
                if prod[0] == '.':   # epsilon production
                    new_action = "reducir " + token + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))

                if (i, "$") in action and new_action not in action[i, "$"]:
                        action[i, "$"].append(new_action)
                elif (i, "$") not in action:
                    action[i, "$"] = [new_action]

        for token, prod, terminal in C[i]:
            if token != start_token and pos_dot == len(prod) - 1:
                if prod[0] == '.':  # epsilon production
                    new_action = "reducir " + token + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))

                for t in terminal:
                    if (i, t) in action and new_action not in action[i, t]:
                            action[i, t].append(new_action)
                    elif (i, t) not in action:
                        action[i, t] = [new_action]
            elif token == start_token and pos_dot == len(prod) - 1:
                action[i, "$"] = ["aceptar"]

    for i in range(len(C)):
        for token in terminal_tokens:
            if (i, token) not in action:
                action[i, token] = ["ERROR"]
            else:
                print("action[", i, " ,", token, "] =", action[i, token])

    return action

def go_to_table(first_set, C, terminal_tokens, non_terminal_tokens, productions):
    ir_a = dict()
    #conj_LR0(start_token, non_terminal_tokens, productions)
    for i in range(len(C)):
        for token_no_terminal in non_terminal_tokens:
            sucesor_token = sucesor(C[i], token_no_terminal, first_set, terminal_tokens, non_terminal_tokens, productions)
            if sucesor_token in C:
                ir_a[i, token_no_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in non_terminal_tokens | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"
            else:
                print("ir_a[", i, ", ", token, "]", ir_a[i, token])

    return ir_a


def create_automaton(first_set, C, terminal_tokens, non_terminal_tokens, productions):
    edges = dict()
    for I in C:
        for token in terminal_tokens | non_terminal_tokens:
            sucesor_token = sucesor(I, token, first_set, terminal_tokens, non_terminal_tokens, productions)
            if sucesor_token in C:
                edges[str(C.index(I)), str(C.index(sucesor_token))] = token

    return edges