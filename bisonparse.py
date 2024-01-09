"""
Filename:
Author: Laura González Pizarro
Description:
"""
import bisonlex
import bisonparse
import re
import grammar
from ply import *

tokens = bisonlex.tokens
start = 'bison'

# Parametros de una gramatica
token_inicial = ""
terminals = set()
non_terminals = set()
producciones = dict()

aux_symbols = set()


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
    global terminals
    terminals |= set(p[2])

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
            terminals.add(token)

def p_declaracion_tokens(p):
    ''' declaracion  : declaracion_tipo listaTokens '''
    if p[1] != "%type":
        for token in p[2]:
            terminals.add(token)

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
                  | LITERAL '''
    p[0] = [p[1]]


def p_expresion_prec(p):
    ''' expresion : prec '''
    p[0] = [p[1]]


def p_expresion_epsilon(p):
    ''' expresion : empty '''


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

    non_terminals.add(p[1])

    for production in p[3]:
        if production is not None:
            for symbol in production:
                aux_symbols.add(symbol)
                if pattern.fullmatch(symbol):           # es un char o string
                    terminals.add(symbol)


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
    if aux_symbols.difference(terminals).difference(non_terminals) != set():
        print("token ilegales: ", aux_symbols.difference(terminals).difference(non_terminals))
        #raise SyntaxError(f'Syntax error at {p.value[0]} {p.lineno} {p.lexpos}')
    p[0] = grammar.Grammar(token_inicial, terminals, non_terminals, producciones)


def p_error(p): #fixme
    raise Exception(f'{p.lexpos}')


yacc.yacc()
