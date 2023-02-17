def leer_flex_fichero(nomb_fich):
    f = open(nomb_fich, "r")
    s = f.read().rstrip()
    print(s)


def leer_flex(s):
    print(s)
def leer_bison_fichero(nomb_fich):
    f = open(nomb_fich, "r")
    s = f.read().rstrip()
    print(s)

def leer_bison(s):
    print(s)


leer_bison_fichero("fichero.txt")
