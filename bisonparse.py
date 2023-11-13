
# --- Parser
import bisonlex
import bisonparse
import re
from ply import *

tokens = bisonlex.tokens

# TODO mirar si se meten producciones repetidas

start = 'bison'

# Parametros de una gramatica
token_inicial = ""
tokens_terminales = set()
tokens_no_terminales = set()
producciones = dict()

tokens_aux = set()

def p_prec(p):
    ''' prec : PREC TOKENID
             | PREC LITERAL '''
    # ignoramos prec
    p[0] = p[2]

def p_start(p):
    ''' start : START TOKENID '''
    bisonparse.token_inicial = p[2]

def p_token(p):
    ''' token : TOKEN listaTokens'''
    global tokens_terminales
    tokens_terminales |= set(p[2])

def p_declaracion_tipo(p):
    ''' declaracion_tipo : LEFT
                         | RIGHT
                         | NONASSOC
                         | PRECEDENCE
                         | TYPE
                         | NTERM '''
    p[0] = p[1]

def p_tipo_dato(p):
    ''' tipo_dato : '<' TOKENID '>' '''

def p_declaracion(p):
    ''' declaracion  : start
                     | token '''

def p_declaracion_tokens_tipo(p):
    ''' declaracion  : declaracion_tipo tipo_dato listaTokens'''
    if p[1] != "%type":
        for token in p[3]:
            tokens_terminales.add(token)

def p_declaracion_tokens(p):
    ''' declaracion  : declaracion_tipo listaTokens '''
    if p[1] != "%type":
        for token in p[2]:
            tokens_terminales.add(token)

def p_declaraciones_declaracion(p):
    ''' declaraciones : declaracion declaraciones
                      | declaracion '''


def p_listaTokens(p):
    ''' listaTokens : listaTokens TOKENID
                    | listaTokens LITERAL '''
    p[1].append(p[2])
    p[0] = p[1]


def p_listaTokens_token(p):
    ''' listaTokens : TOKENID
                    | LITERAL '''
    p[0] = [p[1]]

def p_empty(p):
    ''' empty : '''


def p_expresion_expresion(p):
    ''' expresion : expresion TOKENID
                  | expresion LITERAL '''
    p[1].append(p[2])
    p[0] = p[1]


def p_expresion(p):
    ''' expresion : TOKENID
                  | LITERAL
                  | prec '''
    p[0] = [p[1]]

def p_expresion_epsilon(p):
    ''' expresion :  empty '''


def p_listaExpresiones(p):
    ''' listaExpresiones : expresion '''
    p[0] = [p[1]]


def p_listaExpresiones_expresion(p):
    ''' listaExpresiones : listaExpresiones '|' expresion '''
    p[1].append(p[3])
    p[0] = p[1]


def p_produccion(p):
    ''' produccion    : TOKENID ':' listaExpresiones ';' '''
    p[0] = (p[1], p[3])

    if p[1] in producciones:
        for prod in p[3]:
            if prod not in producciones[p[1]]:
                producciones[p[1]].append(prod)
    else:
        producciones[p[1]] = p[3]

    pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')

    tokens_no_terminales.add(p[1])

    for produccion in p[3]:
        if produccion is not None:
            for token in produccion:
                tokens_aux.add(token)
                if pattern.fullmatch(token):           # es un char o string
                    tokens_terminales.add(token)
                #elif (not pattern.fullmatch(token)) and token not in tokens_terminales:  # es un no terminal
                #    tokens_no_terminales.add(token)


def p_listaProducciones(p):
    ''' listaProducciones : listaProducciones produccion '''
    p[1].append(p[2])
    p[0] = p[1]

def p_listaProducciones_produccion(p):
    ''' listaProducciones : produccion '''
    p[0] = [p[1]]


def p_reglas(p):
    ''' reglas : EUNG listaProducciones '''
    if bisonparse.token_inicial == "":
        bisonparse.token_inicial = p[2][0][0]


def p_bison(p):
    ''' bison : declaraciones  reglas
              | reglas '''

    if tokens_aux.difference(tokens_terminales).difference(tokens_no_terminales) != set():
        print("token ilegales: ", tokens_aux.difference(tokens_terminales).difference(tokens_no_terminales))

    p[0] = (token_inicial, tokens_terminales, tokens_no_terminales, producciones)


def p_error(p): #fixme
    raise SyntaxError(f'Syntax error at {p}')


yacc.yacc()
