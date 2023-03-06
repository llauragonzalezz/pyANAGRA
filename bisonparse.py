
# --- Parser
import bisonlex
import bisonparse
import re
from ply import *

tokens = bisonlex.tokens

start = 'bison'

# Parametros de una gramatica
token_inicial = ""
tokens_terminales = []
tokens_no_terminales = []
producciones = dict()

def p_prec(p):
    ''' prec : PREC TOKENID
             | PREC LITERAL '''
    # ignoramos prec
    p[0] = p[2]


def p_start(p):
    ''' start : START TOKENID '''
    bisonparse.primera_regla = p[2]

def p_declaracion_tipo(p):
    ''' declaracion_tipo : LEFT
                         | RIGHT
                         | NONASSOC
                         | PRECEDENCE
                         | TYPE
                         | TOKEN
                         | NTERM '''

def p_tipo_dato(p):
    '''
    tipo_dato : '<' TOKENID '>'
    '''

def p_declaracion(p):
    ''' declaracion  : start
                     | declaracion_tipo tipo_dato listaTokens
                     | declaracion_tipo listaTokens '''
    # ya se hace en sus respectivas funciones


def p_declaraciones_declaracion(p):
    ''' declaraciones : declaracion declaraciones
                      | declaracion '''


def p_listaTokens(p):
    ''' listaTokens : listaTokens TOKENID '''
    p[1].append(p[2])
    p[0] = p[1]


def p_listaTokens_token(p):
    ''' listaTokens : TOKENID
                    | LITERAL '''
    p[0] = [p[1]]

def p_empty(p):
    ''' empty : EMPTY
              | '''


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
def p_listaExpresiones(p):
    ''' listaExpresiones : expresion
                         | empty '''
    p[0] = [p[1]]

def p_listaExpresiones_expresion(p):
    ''' listaExpresiones : listaExpresiones '|' expresion '''
    p[1].append(p[3])
    p[0] = p[1]


def p_produccion(p):
    ''' produccion    : TOKENID ':' listaExpresiones ';' '''
    p[0] = (p[1], p[3])
    producciones[p[1]] = p[3]
    es_terminal = True
    pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')
    for produccion in p[3]:
        if produccion is not None:
            for token in produccion:
                if not pattern.fullmatch(token):
                    es_terminal = False
                    break
        if not es_terminal:
            break

    if es_terminal and p[1] not in tokens_terminales and p[1] not in tokens_no_terminales:
        # añadimos a terminales
        tokens_terminales.append(p[1])
    elif not es_terminal:
        if p[1] in tokens_terminales: # si esta en terminales lo borramos
            tokens_terminales.remove(p[1])
        # añadimos a no terminales
        tokens_no_terminales.append(p[1])



def p_listaProducciones(p):
    ''' listaProducciones : listaProducciones produccion '''
    p[1].append(p[2])
    p[0] = p[1]

def p_listaProducciones_produccion(p):
    ''' listaProducciones : produccion '''
    p[0] = [p[1]]


def p_reglas(p):
    ''' reglas : EUNG listaProducciones EUNG '''
    if bisonparse.token_inicial == "":
        bisonparse.token_inicial = p[2][0][0]

def p_bison(p):
    ''' bison : declaraciones  reglas
              | reglas '''
    print("token_inicial", token_inicial)
    print("tokens_terminales", tokens_terminales)
    print("tokens_no_terminales", tokens_no_terminales)
    print("producciones", producciones)

def p_error(p):
    print(f'Syntax error at {p.value!r}')


yacc.yacc(debug=True)
