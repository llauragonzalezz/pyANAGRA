
import bisonparse
import re
def eliminacion_no_terminales():
    viejo = []
    nuevo = []

    for noTerminal in bisonparse.tokens_no_terminales:
        for produccion in bisonparse.producciones[noTerminal]:
            if (produccion in bisonparse.tokens_terminales) or (produccion is None):
                nuevo.append(produccion)
                break

    while viejo != nuevo:
        viejo = nuevo
        nuevo = viejo
        for noTerminal in bisonparse.tokens_no_terminales:
            for produccion in bisonparse.producciones[noTerminal]:
                if produccion not in nuevo and ((produccion in bisonparse.tokens_terminales) or (produccion in viejo)):
                    nuevo.append(produccion)
                    break

    bisonparse.tokens_terminales = nuevo
    for nuevo_no_terminal in nuevo:
        for produccion in bisonparse.producciones[nuevo_no_terminal]:
            print()

def eliminacion_no_accesibles():
    viejo = [bisonparse.token_inicial]
    nuevo = []
    print()

def factorizacion_a_izquierda():
    print()


def eliminacion_no_terminables_no_derivables():
    viejo = []
    nuevo = []

    pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')

    for noTerminal in bisonparse.tokens_no_terminales:
        solo_terminales = True
        for produccion in bisonparse.producciones[noTerminal]:
            if not ((produccion in bisonparse.tokens_terminales) or (produccion in bisonparse.tokens_no_terminales)):
                solo_terminales = False
                break

        if solo_terminales:
            nuevo.append(noTerminal)
    print()

def eliminacion_producciones_epsilon():
    print()

def eliminacion_ciclos():
    print()


def conjunto_primero():
    print()

def conjunto_siguiente():
    print()