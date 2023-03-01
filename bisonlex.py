import sys

# left          : LEFT listaTokens
#
# precedence    : PRECEDENCE listaTokens
#
# prec          : PREC TOKENID        # especial(unitario)
#
# start         : START TOKENID
#
# right         : RIGHT listaTokens
#
# nonassoc      : NONASSOC listaTokens
#
# type          : TYPE listaTokens
#
# nterm         : NTERM listaTokens
#
# token         : TOKEN listaTokens
#
# listaTokens   : listaTokens TOKENID
#               | TOKENID
#
# empty         : EMPTY
#               |
#
# expresion     : TOKENID expresion
#               | CARACTER expresion
#               | TOKENID
#               | CARACTER
#
#
# listaExpresiones: listaExpresiones OR expresion
#               | epresion
#               | empty
#
# produccion    : TOKENID TD listaExpresiones SM
#
# listaProducciones: produccion listaProducciones
#               | produccion
#
# declaracion   : start
#               | precedence
#               | right
#               | left
#               | nonassoc
#               | type
#               | nterm
#               | token
#
# declaraciones : declaracion declaraciones
#               | declaracion
#
# reglas        : EUNG listaProducciones EUNG
#
#
# bison         : #prologo -> por ahora no
#                 declaraciones
#                 reglas
#                 #epilogo -> por ahora no


from ply import lex
from ply import yacc
# All tokens must be named in advance.
tokens = ('LEFT', 'RIGHT', 'NONASSOC', 'PRECEDENCE', 'PREC', 'EUNG', 'LITERAL',
          'START', 'NTERM',  'TYPE', 'TOKEN',  'TOKENID', 'EMPTY', 'UNION')

# Ignored characters
literals = [';', '|', ':', '<', '>']

t_ignore = ' \t'

# Token matching rules are written as regexs
t_LEFT = r'%left'
t_RIGHT = r'%right'
t_NONASSOC = r'%nonassoc'
t_PRECEDENCE = r'%precedence'
t_PREC = r'%prec'
t_START = r'%start'
t_NTERM = r'%nterm'
t_TYPE = r'%type'
t_TOKEN = r'%token'
t_EUNG = r'%%'
t_UNION = r'%union'
t_TOKENID = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_EMPTY = r'%empty'
t_LITERAL = r'''(?P<quote>['"]).*?(?P=quote)'''


# A function can be used if there is an associated action.
# Write the matching regex in the docstring.
# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += 1

def t_comment(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


t_ignore_comment = r'//.*'


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    print(t.value)
    t.lexer.skip(1)

lex.lex()

if __name__ == '__main__':
    lex.runmain()

