import conjuntos
def ampliar_gramatica(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    nuevo_token_inicial = token_inicial + "*"
    tokens_no_terminales |= {nuevo_token_inicial}
    producciones[nuevo_token_inicial] = [['.', token_inicial]]
    #I = clausura(producciones[nuevo_token_inicial], tokens_no_terminales, producciones)
    print(conj_LR0(nuevo_token_inicial, tokens_no_terminales, producciones))
    tabla_accion(nuevo_token_inicial, tokens_terminales, tokens_no_terminales, producciones)

    return nuevo_token_inicial, tokens_no_terminales, producciones




def clausura(I, tokens_no_terminales, producciones):
    viejo = []
    nuevo = I
    while viejo != nuevo:
        viejo = nuevo
        for prod in viejo:
            if prod.index('.') < len(prod) - 1 and prod[prod.index('.')+1] in tokens_no_terminales:
                for prod_B in producciones[prod[prod.index('.')+1]]:
                    if ['.'] + prod_B not in nuevo:
                        nuevo.append(['.'] + prod_B)
    return nuevo


def sucesor(I, token, tokens_no_terminales, producciones):
    S = []
    for prod in I:
        pos_punto = prod.index('.')
        if pos_punto < len(prod) - 1 and prod[pos_punto + 1] == token:
            S.append(prod[:pos_punto] + [prod[pos_punto + 1]] + ['.'] + prod[pos_punto+2:])
            if prod.index('.') < len(prod) - 2 and prod[prod.index('.')+2] in tokens_no_terminales:
                for prof_token in producciones[prod[prod.index('.')+2]]:
                    S.append(['.'] + prof_token)

    return clausura(S.copy(), tokens_no_terminales, producciones)


def conj_LR0(token_inicial, tokens_no_terminales, producciones):
    viejo = []
    nuevo = [clausura(producciones[token_inicial], tokens_no_terminales, producciones)]
    while viejo != nuevo:
        viejo = nuevo
        for I in nuevo:
            #print("I: ", I)
            prods = {token for prod in I for token in prod if token != '.' }
            #print("prods: ", prods)
            for token in prods:
                #print("token:", token)
                sucesor_token = sucesor(I, token, tokens_no_terminales, producciones)
                #print("sucesor_token: ", sucesor_token)
                if sucesor_token != [] and sucesor_token not in nuevo:
                    nuevo.append(sucesor_token)
                    #print("nuevo tras añadir:", nuevo)

    return nuevo


def tabla_accion(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    accion = dict()
    follow_set = conjuntos.calculate_follow_set(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    for token in tokens_no_terminales:
        print("Sig(", token, ") = ", follow_set[token])

    C = [[['.', 'E'], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['E', '.'], ['E', '.', "'+'", 'T']],
         [['T', '.']],
         [["'('", '.', 'E', "')'"], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['id', '.']],
         [['E', "'+'", '.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [["'('", 'E', '.', "')'"], ['E', '.', "'+'", 'T']],
         [['E', "'+'", 'T', '.']],
         [["'('", 'E', "')'", '.']]]
    for i in range(len(C)):
        print("i:", i)
        for token_terminal in tokens_terminales:
            for prod in C[i]:
                if prod.index('.') < len(prod) - 1 and prod[prod.index('.') + 1] == token_terminal:
                    sucesor_i_token_terminal = sucesor(C[i], token_terminal, tokens_no_terminales, producciones)
                    if sucesor_i_token_terminal in C:
                        accion[i, token_terminal] = "desplazar " + str(C.index(sucesor_i_token_terminal))
                if prod.index('.') == len(prod) - 1:
                    accion[i, "$"] = "reducir " + "{} → {}".format(token_no_terminal, " ".join(str(x) for x in prod[:-1]))

        for token_no_terminal in tokens_no_terminales.difference({token_inicial}):
            for prod in C[i]:
                if [x for x in prod if x != '.'] in producciones[token_no_terminal] and prod.index('.') == len(prod) - 1:
                    for token_no_terminal_siguiente in follow_set[token_no_terminal]:   # todo no se por que no me van bien las producciones a veces:
                        accion[i, token_no_terminal_siguiente] = "reducir " + "{} → {}".format(token_no_terminal, " ".join(str(x) for x in prod[:-1]))

        for I in C:
            if [token_inicial[:-1], '.'] in I:
                accion[C.index(I), "$"] = "aceptar"

    for i in range(len(C)):
        for token in tokens_no_terminales | tokens_terminales | {"$"}:
            if (i, token) not in  accion:
                accion[i, token] = "ERROR"
            else:
                print("accion[", i, " ,", token, "] =", accion[i, token])
    return accion

def tabla_ir_a(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()


def algoritmo(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()