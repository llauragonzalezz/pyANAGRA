import re
import conjuntos


def ampliar_gramatica(token_inicial, tokens_no_terminales, producciones):
    nuevo_token_inicial = token_inicial + "*"
    tokens_no_terminales |= {nuevo_token_inicial}
    producciones[nuevo_token_inicial] = [['.', token_inicial]]
    # I = clausura(producciones[nuevo_token_inicial], tokens_no_terminales, producciones)
    # print(conj_LR0(nuevo_token_inicial, tokens_no_terminales, producciones))
    #simulate(accion, ir_a, "id '+' id" + " $")
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
            prods = {token for prod in I for token in prod if token != '.' }
            for token in prods:
                sucesor_token = sucesor(I, token, tokens_no_terminales, producciones)
                if sucesor_token != [] and sucesor_token not in nuevo:
                    nuevo.append(sucesor_token)

    return nuevo


def tabla_accion(token_inicial, tokens_terminales, tokens_no_terminales, producciones):
    accion = dict()
    follow_set = conjuntos.calculate_follow_set(token_inicial, tokens_terminales, tokens_no_terminales, producciones)
    C = [[['.', 'E'], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['E', '.'], ['E', '.', "'+'", 'T']],
         [['T', '.']],
         [["'('", '.', 'E', "')'"], ['.', 'E', "'+'", 'T'], ['.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [['id', '.']],
         [['E', "'+'", '.', 'T'], ['.', "'('", 'E', "')'"], ['.', 'id']],
         [["'('", 'E', '.', "')'"], ['E', '.', "'+'", 'T']],
         [['E', "'+'", 'T', '.']],
         [["'('", 'E', "')'", '.']]]
    #conj_LR0(token_inicial, tokens_no_terminales, producciones)
    for i in range(len(C)):
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
        for token in tokens_terminales | {"$"}:
            if (i, token) not in accion:
                accion[i, token] = "ERROR"
    return accion


def tabla_ir_a(token_inicial, tokens_no_terminales, producciones):
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
    #conj_LR0(token_inicial, tokens_no_terminales, producciones)
    for i in range(len(C)):
        for token_no_terminal in tokens_no_terminales:
            sucesor_token = sucesor(C[i], token_no_terminal, tokens_no_terminales, producciones)
            if sucesor_token in C:
                ir_a[i, token_no_terminal] = C.index(sucesor_token)

    for i in range(len(C)):
        for token in tokens_no_terminales | {"$"}:
            if (i, token) not in ir_a:
                ir_a[i, token] = "ERROR"
    return ir_a


def simulate(accion, ir_a, input):
    aceptado = False
    error = False
    stack = [0]
    elementos = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', input)
    print("elementos: ", elementos)
    it = iter(elementos)
    n = next(it)

    if n == "'":  # if sig_tok is character or string TODO poner tambien si es string "
        y = next(it)
        if y != "'":
            n += y
        else:
            n += y + next(it)
    print("n: ", n)
    while not (aceptado or error):
        s = int(stack[len(stack) - 1])
        if accion[s, n][:9] == "desplazar":
            print("tabla_accion[", s, ",", n, "] = ", accion[s, n])
            stack.append(n)
            stack.append(accion[s, n][10:])
            print("añado: ", n)
            print("añado: ", accion[s, n][10:])
            print("stack despues de añadir: ", stack)
            n = next(it)
            if n == "'":  # if sig_tok is character or string TODO poner tambien si es string "
                y = next(it)
                if y != "'":
                    n += y
                else:
                    n += y + next(it)
            print("n: ", n)

        elif accion[s, n] == "aceptar":
            print("tabla_accion[", s, ",", n, "] = ", accion[s, n])
            aceptado = True
        elif accion[s, n] == "ERROR":
            print("tabla_accion[", s, ",", n, "] = ", accion[s, n])
            error = True
        elif accion[s, n][:7] == "reducir":
            print("tabla_accion[", s, ",", n, "] = ", accion[s, n])
            partes = accion[s, n][8:].split("→")
            print("stack: ", stack)
            for i in range(2*len(partes[1].strip().split())):
                print("hago pop")
                stack.pop()
            print("stack despues de borrar: ", stack)
            s = int(stack[len(stack) - 1])
            print("añado: ", partes[0][0])
            print("añado", ir_a[s, partes[0][0]])
            stack.append(partes[0][0])
            stack.append(ir_a[s, partes[0][0]])
            print("stack despues de añadir: ", stack)
