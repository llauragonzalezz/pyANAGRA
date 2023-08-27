import LR

def conj_LR1(first_set, start_token, terminal_tokens, non_terminal_tokens, productions):
    old = []
    new = [LR.clausura([(start_token, prod, {'$'}) for prod in productions[start_token]], first_set, terminal_tokens,
                    non_terminal_tokens, productions)]
    conjunto_I = []
    diccionario = dict()
    while old != new:
        old = new
        for I in new:
            prods = {token for _, prod, _ in I for token in prod if token != '.'}
            for token in prods:
                if (I, token) not in conjunto_I:
                    conjunto_I.append((I, token))
                    diccionario[len(conjunto_I) - 1, token] = LR.sucesor(I, token, first_set, terminal_tokens,
                                                                      non_terminal_tokens, productions)
                    sucesor_token = diccionario[len(conjunto_I) - 1, token]
                else:
                    sucesor_token = diccionario[conjunto_I.index((I, token)), token]

                if sucesor_token != [] and sucesor_token not in new:
                    aniadir = True
                    for i, c in enumerate(new):
                        if len(c) == len(sucesor_token):
                            for j in range(len(sucesor_token)):
                                if c[j][0] != sucesor_token[j][0] or c[j][1] != sucesor_token[j][1]:
                                    break
                            else:
                                aniadir = False
                                break

                    if aniadir:
                        new.append(sucesor_token)
                    else:
                        new[i] = []
                        for j in range(len(sucesor_token)):
                            if c[j][2] - sucesor_token[j][2] == c[j][2]:
                                print(c[j][2], sucesor_token[j][2], c[j][2] | sucesor_token[j][2])

                                new[i].append((c[j][0], c[j][1], c[j][2] | sucesor_token[j][2]))
                            else:
                                new[i].append((c[j][0], c[j][1], c[j][2]))
    for entrada in new:
        print(entrada)
    return new

def action_table(first_set, C, start_token, terminal_tokens, non_terminal_tokens, productions):
    action = dict()

    for i in range(len(C)):
        for token, prod, terminal in C[i]:
            pos_dot = prod.index('.')
            if pos_dot < len(prod) - 1 and prod[pos_dot + 1] in terminal_tokens:
                terminal_token = prod[pos_dot + 1]
                sucesor_i_token_terminal = LR.sucesor(C[i], terminal_token, first_set, terminal_tokens, non_terminal_tokens, productions)
                aniadir = False
                for j, c in enumerate(C):  # find c tq sucesor_token <= c
                    if len(c) == len(sucesor_i_token_terminal):
                        for k in range(len(sucesor_i_token_terminal)):
                            if c[k][0] != sucesor_i_token_terminal[k][0] or c[k][1] != sucesor_i_token_terminal[k][1]:
                                break
                        else:
                            aniadir = True
                            break

                if aniadir:
                    new_action = "desplazar " + str(j)
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
            sucesor_token = LR.sucesor(C[i], token_no_terminal, first_set, terminal_tokens, non_terminal_tokens, productions)
            aniadir = False
            for j, c in enumerate(C):  # find c tq sucesor_token <= c
                if len(c) == len(sucesor_token):
                    for k in range(len(sucesor_token)):
                        if c[k][0] != sucesor_token[k][0] or c[k][1] != sucesor_token[k][1]:
                            break
                    else:
                        aniadir = True
                        break

            if aniadir:
                ir_a[i, token_no_terminal] = j

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
            sucesor_token = LR.sucesor(I, token, first_set, terminal_tokens, non_terminal_tokens, productions)
            aniadir = False
            for i, c in enumerate(C): # find c tq sucesor_token <= c
                if len(c) == len(sucesor_token):
                    for j in range(len(sucesor_token)):
                        if c[j][0] != sucesor_token[j][0] or c[j][1] != sucesor_token[j][1]:
                            break
                    else:
                        aniadir = True
                        break

            if aniadir:
                edges[str(C.index(I)), str(i)] = token

    return edges