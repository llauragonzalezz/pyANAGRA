import LR

def conj_LR1(first_set, start_token, terminal_tokens, non_terminal_tokens, productions):
    new = [LR.clausura([(start_token, prod, {'$'}) for prod in productions[start_token]], first_set, terminal_tokens,
                    non_terminal_tokens, productions)]
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
                    diccionario[len(conjunto_I) - 1, token] = LR.sucesor(I, token, first_set, terminal_tokens,
                                                                      non_terminal_tokens, productions)
                    sucesor_token = diccionario[len(conjunto_I) - 1, token]
                else:
                    sucesor_token = diccionario[conjunto_I.index((I, token)), token]

                if sucesor_token != [] and sucesor_token not in new:
                    aniadir = True
                    for i, c in enumerate(new):
                        if len(c) == len(I):
                            for j in range(len(I)):
                                if c[j][0] != sucesor_token[j][0] or c[j][1] != sucesor_token[j][1]:
                                    break
                            else:
                                aniadir = False
                                break

                    if aniadir:
                        new.append(sucesor_token)
                    else:
                        new[i] = []
                        for j in range(len(I)):
                            new[i].append((c[j][0], c[j][1], c[j][2] | sucesor_token[j][2]))
                    bool_new = True

    for entrada in new:
        print(entrada)
    return new

def conj_LR1_bis(first_set, start_token, terminal_tokens, non_terminal_tokens, productions):
    conj = LR.conj_LR1(first_set, start_token, terminal_tokens, non_terminal_tokens, productions)
    new_conj = []
    for I in conj:
        aniadir = True
        for i, c in enumerate(new_conj):
            if len(c) == len(I):
                for j in range(len(I)):
                    if c[j][0] != I[j][0] or c[j][1] != I[j][1]:
                        break
                else:
                    aniadir = False
                    break

        if aniadir:
            new_conj.append(I)
        else:
            new_conj[i] = []
            for j in range(len(I)):
                new_conj[i].append((c[j][0], c[j][1], c[j][2] | I[j][2]))

    for entrada in new_conj:
        print(entrada)
    return new_conj

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