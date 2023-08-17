
def ampliar_gramatica(token_inicial, tokens_no_terminales, producciones):
    nuevo_token_inicial = token_inicial + "*"
    tokens_no_terminales |= {nuevo_token_inicial}
    producciones[nuevo_token_inicial] = [['.', token_inicial]]
    clausura(nuevo_token_inicial, tokens_no_terminales, producciones)
    return nuevo_token_inicial, tokens_no_terminales, producciones


def clausura(token_inicial, tokens_no_terminales, producciones):
    viejo = []
    nuevo = producciones[token_inicial]

    while viejo != nuevo:
        print("nuevo: ", nuevo)
        print("viejo: ", viejo)
        viejo = nuevo
        for prod in viejo:
            print("prod: ", prod)
            if prod[prod.index('.')+1] in tokens_no_terminales:
                for prod_B in producciones[prod[prod.index('.')+1]]:
                    print("prod_B: ", prod_B)
                    if ['.'] + prod_B not in nuevo:
                        print("añado: ", ['.'] + prod_B)
                        nuevo.append(['.'] + prod_B)
                        print("nuevo queda así: ", nuevo)

    print(nuevo)
    return nuevo
def sucesor(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()

def tabla_accion(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()

def tabla_ir_a(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()

def algoritmo(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    print()