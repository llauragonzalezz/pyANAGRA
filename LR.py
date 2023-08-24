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

    #C = conj_LR_1(start_token_extended, terminal_tokens | {'$'}, non_terminal_tokens, productions)
    #action_table(C, start_token, terminal_tokens | {'$'}, non_terminal_tokens, productions)
    #go_to_table(C, terminal_tokens | {'$'}, non_terminal_tokens, productions)
    #I = clausura([(start_token_extended, ['.', start_token], {'$'})], terminal_tokens | {'$'}, non_terminal_tokens, productions)
    #uno = sucesor(I.copy(), terminal_tokens, "S", non_terminal_tokens, productions)
    #dos = sucesor(I.copy(), terminal_tokens, "C", non_terminal_tokens, productions)
    #tres = sucesor(I.copy(), terminal_tokens, "c", non_terminal_tokens, productions)
    #cuatro = sucesor(I.copy(), terminal_tokens, "d", non_terminal_tokens, productions)
    #cinco = sucesor(dos.copy(), terminal_tokens, "C", non_terminal_tokens, productions)
    #seis = sucesor(dos.copy(), terminal_tokens, "c", non_terminal_tokens, productions)
    #seis_bis = sucesor(seis.copy(), terminal_tokens, "c", non_terminal_tokens, productions)
    #siete = sucesor(dos.copy(), terminal_tokens, "d", non_terminal_tokens, productions)
    #siete_bis = sucesor(seis.copy(), terminal_tokens, "d", non_terminal_tokens, productions)
    #ocho = sucesor(tres.copy(), terminal_tokens, "C", non_terminal_tokens, productions)
    #nueve = sucesor(seis.copy(), terminal_tokens, "C", non_terminal_tokens, productions)

def clausura(I, terminal_tokens, non_terminal_tokens, productions):
    first_set = conj.calculate_first_set(terminal_tokens, non_terminal_tokens, productions)
    viejo = []
    nuevo = I

    while viejo != nuevo:
        viejo = nuevo
        for token, prod, terminal in viejo:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] in non_terminal_tokens: # A -> α.Bþ, {terminal}
                for prod_B in productions[prod[prod.index('.') + 1]]: # B -> y
                    first_set_token = set()
                    if prod.index('.') < len(prod) - 2:  # Pri(þ)
                        first_set_token = first_set[prod[prod.index('.') + 2]]
                        if prod[prod.index('.') + 2] in non_terminal_tokens and op.is_nullable(prod[prod.index('.') + 2], non_terminal_tokens, productions):  # þ -> eps => Pri(a)
                            first_set_token |= terminal
                    if prod.index('.') >= len(prod) - 2:  # Si no existe þ => Pri(a)
                        first_set_token = terminal
                    for b in terminal_tokens & first_set_token:
                        if prod_B is None and (prod[prod.index('.') + 1], ['.'], {b}) not in nuevo:
                            nuevo.append((prod[prod.index('.') + 1], ['.'], {b}))
                        elif prod_B is not None and (prod[prod.index('.') + 1], ['.'] + prod_B, {b}) not in nuevo:
                            nuevo.append((prod[prod.index('.') + 1], ['.'] + prod_B, {b}))

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

def sucesor(I, token, terminal_tokens, non_terminal_tokens, productions):
    S = []
    for token_prod, prod, terminal in I:
        pos_dot = prod.index('.')
        if pos_dot < len(prod) - 1 and prod[pos_dot + 1] == token:
            S.append((token_prod, prod[:pos_dot] + [prod[pos_dot + 1]] + ['.'] + prod[pos_dot + 2:], terminal))
            if prod.index('.') < len(prod) - 2 and prod[prod.index('.') + 2] in non_terminal_tokens:
                for prod_token in productions[prod[prod.index('.') + 2]]:
                    if prod_token is None:
                        S.append((prod[prod.index('.') + 2], ['.'], terminal))
                    else:
                        S.append((prod[prod.index('.') + 2], ['.'] + prod_token, terminal))

    return clausura(S.copy(), terminal_tokens, non_terminal_tokens, productions)


def conj_LR1(start_token, terminal_tokens, non_terminal_tokens, productions):
    old = []
    new = [clausura([(start_token, prod, {'$'}) for prod in productions[start_token]], terminal_tokens, non_terminal_tokens, productions)]
    while old != new: # poner booleano
        old = new
        for I in new:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            for token in prods:
                sucesor_token = sucesor(I, token, terminal_tokens, non_terminal_tokens, productions)
                if sucesor_token != [] and sucesor_token not in new:
                    new.append(sucesor_token) # poner booleano a true


    return new

def action_table(C, start_token, terminal_tokens, non_terminal_tokens, productions):
    action = dict()

    for i in range(len(C)):
        for token, prod, terminal in C[i]:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] in terminal_tokens:
                terminal_token = prod[prod.index('.') + 1]
                sucesor_i_token_terminal = sucesor(C[i], terminal_token, terminal_tokens, non_terminal_tokens, productions)
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

        for token, prod, terminal in C[i]:
            if token != start_token and prod.index('.') == len(prod) - 1:
                if prod[0] == '.':  # epsilon production
                    new_action = "reducir " + token + "  → ε"
                else:
                    new_action = "reducir " + "{} → {}".format(token, " ".join(str(x) for x in prod[:-1]))

                for t in terminal:
                    if (i, t) in action and new_action not in action[i, t]:
                            action[i, t].append(new_action)
                    elif (i, t) not in action:
                        action[i, t] = [new_action]
            elif token == start_token and prod.index('.') == len(prod) - 1:
                action[i, "$"] = ["aceptar"]

    for i in range(len(C)):
        for token in terminal_tokens:
            if (i, token) not in action:
                action[i, token] = ["ERROR"]
            else:
                print("action[", i, " ,", token, "] =", action[i, token])

    return action

def go_to_table(C, terminal_tokens, non_terminal_tokens, productions):
    ir_a = dict()
    #conj_LR0(start_token, non_terminal_tokens, productions)
    for i in range(len(C)):
        for token_no_terminal in non_terminal_tokens:
            sucesor_token = sucesor(C[i], token_no_terminal, terminal_tokens, non_terminal_tokens, productions)
            if sucesor_token in C:
                ir_a[i, token_no_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in non_terminal_tokens | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"
            else:
                print("ir_a[", i, ", ", token, "]", ir_a[i, token])

    return ir_a


def create_automaton(C, terminal_tokens, non_terminal_tokens, productions):
    edges = dict()
    for I in C:
        for token in terminal_tokens | non_terminal_tokens:
            sucesor_token = sucesor(I, token, terminal_tokens, non_terminal_tokens, productions)
            if sucesor_token in C:
                edges[str(C.index(I)), str(C.index(sucesor_token))] = token

    return edges