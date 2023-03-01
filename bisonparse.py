
# --- Parser
import bisonlex
tokens = bisonlex.tokens

from ply import *

start = 'bison'


def p_prec(p):
    ''' prec : PREC TOKENID
             | PREC LITERAL '''
    # ignoramos prec
    p[0] = p[2]


def p_start(p):
    ''' start : START TOKENID '''
    print("start = ", p[2])


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
    print(p[1], p[3])

def p_listaProducciones(p):
    ''' listaProducciones : listaProducciones produccion '''
    p[1].append(p[2])
    p[0] = p[1]

def p_listaProducciones_produccion(p):
    ''' listaProducciones : produccion '''
    p[0] = [p[1]]


def p_reglas(p):
    ''' reglas : EUNG listaProducciones EUNG '''
    p[0] = p[2]
    print("primera regla:", p[2][0][0])
    # añadirlo al diccionario


def p_bison(p):
    ''' bison : declaraciones  reglas
              | reglas '''


def p_error(p):
    print(f'Syntax error at {p.value!r}')



yacc.yacc(debug=True)
