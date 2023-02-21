import re

def leer_flex_fichero(nomb_fich):
    f = open(nomb_fich, "r")
    s = f.read().rstrip()
    leer_flex(s)



def leer_patrones(s):
    templates = re.findall(r"(\w+)\s\((\S+)\)", s, re.DOTALL)
    print(templates)
    #TODO crear diccionario para las plantillas <nombreAux: patron>
    patrones = re.findall(r"(\S+\s*(?:\s*\|\s*\S*)*)\s*\{\s*return\s(\w*)", s, re.DOTALL)
    print(patrones)
    for patron in patrones:
        partes_derecha = patron[0].split("|")
        print(patron[1])
        for posibles in partes_derecha:
            posibles = posibles.split()
            print(posibles)
            # TODO comprobar si existe {nombre de alguna plantilla}, si es así, sustituirla por su patrón
        # regla[0] -> key
        # patron[0].split -> values


def leer_flex(s):
    leer_patrones(s)
def leer_bison_fichero(nomb_fich):
    f = open(nomb_fich, "r")
    s = f.read()
    leer_bison(s)


def leer_producciones(s):
    producciones = re.search(r"\w+:[\s\S]+;", s, re.DOTALL).group(0).split(";")
    for produccion in producciones[0:len(producciones) - 1]:
        posibles_partes_derecha = re.findall(r"(\w+):([\s\S]+)", produccion, re.DOTALL)
        print(posibles_partes_derecha[0][0], ": [")
        partes_derecha = posibles_partes_derecha[0][1].split("|")
        # regla[0] -> key
        # posibles[1].split -> values
        for posibles in partes_derecha:
            posibles = posibles.split()
            print("\t", posibles)
            print("%prec" in posibles)
            # if posibles.index("%prec"):
            # TODO: comprobar si hay algun %prec, si es así, darle alguna propiedad al token siquiente
            # y borrar %prec de la lista
        print("]")

def leer_reglas(cadena):
    re_start_token_type_left_right_nonassoc = r"%(start|token|type|left|right|nonassoc)\s+(?:<\w+>)?\s*(\w+\s*\w*)+"
    resultados = re.findall(re_start_token_type_left_right_nonassoc, cadena, re.DOTALL)
    print(resultados)
    for regla in resultados:
        # regla[0] -> key
        # regla[1].split -> values
        print(regla[0], ":", regla[1].split())

def leer_bison(s):
    leer_reglas(s)

    leer_producciones(s)


leer_flex_fichero("fichero.txt")
