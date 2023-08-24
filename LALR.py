import LR

def conj_LR1(start_token, terminal_tokens, non_terminal_tokens, productions):
    conj = LR.conj_LR1(start_token, terminal_tokens, non_terminal_tokens, productions)
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