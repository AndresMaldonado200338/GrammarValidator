# Producciones de tipo 3 o regulares
def is_type3(productions):
    """
    Valida si las producciones de la gramática son de tipo 3 (gramática regular).
    Argumento:
    productions: Diccionario donde las claves son los no terminales (izquierda de la producción)
                 y los valores son listas de las posibles producciones (derecha de la producción).
    Retorno:
    True si la gramática es de tipo 3, False si no lo es.
    """
    left_right = None
    
    for left, rights in productions.items():
        if not (len(left) == 1 and left.isupper()):
            return False

        for right in rights:
            if len(right) == 1 and right.islower():  # A -> a
                continue
            elif len(right) == 2 and right[0].islower() and right[1].isupper():  # A -> aB
                if left_right is None:
                    left_right = "right"
                elif left_right == "left":
                    return False
            elif len(right) == 2 and right[0].isupper() and right[1].islower():  # A -> Ba
                if left_right is None:
                    left_right = "left"
                elif left_right == "right":
                    return False
            else:
                return False
    return True

# Producciones de tipo 2 o libres de contexto
def is_type2(productions):
    """
    Valida si las producciones de la gramática son de tipo 2 (gramática libre de contexto).
    
    Argumento:
    productions: Diccionario donde las claves son los no terminales (izquierda de la producción)
                 y los valores son listas de las posibles producciones (derecha de la producción).
    
    Retorno:
    True si la gramática es de tipo 2, False si no lo es.
    """
    for left, rights in productions.items():
        if not (len(left) == 1 and left.isupper()):
            return False
        for right in rights:
            if right == "":
                return False
    return True