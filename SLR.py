
def ampliar_gramatica(token_inicial, tokens_no_terminales, producciones):
    nuevo_token_inicial = token_inicial + "*"
    tokens_no_terminales |= {nuevo_token_inicial}
    producciones[nuevo_token_inicial] = [['.', token_inicial]]
    I = clausura(producciones[nuevo_token_inicial], tokens_no_terminales, producciones)
    
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
        if prod[pos_punto + 1] == token:
            S.append(prod[:pos_punto] + [prod[pos_punto + 1]] + ['.'] + prod[pos_punto+2:])
            if prod.index('.') < len(prod) - 2 and prod[prod.index('.')+2] in tokens_no_terminales:
                for prof_token in producciones[prod[prod.index('.')+2]]:
                    S.append(['.'] + prof_token)

    return clausura(S.copy(), tokens_no_terminales, producciones)


def conj_LR0(token_inicial, tokens_no_terminales, producciones):
    viejo = []
    nuevo = clausura(producciones[token_inicial], tokens_no_terminales, producciones)
    while viejo != nuevo:
        viejo = nuevo
        for I in nuevo:
            print("I: ", I)
            prods = set(I)
            print("prods: ", prods)
            for token in prods:
                sucesor_token = sucesor(I, token)
                print("sucesor_token: ", sucesor_token)
                if sucesor_token == [] or sucesor_token not in nuevo:
                    nuevo |= sucesor_token
                    print("nuevo tras añadir:", nuevo)
    return nuevo


def tabla_accion(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()


def tabla_ir_a(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()


def algoritmo(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()