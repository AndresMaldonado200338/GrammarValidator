def is_non_terminal(symbol: str) -> bool:
    """Verifica si un símbolo es no terminal (mayúscula de un solo carácter y no ε)."""
    return (
        isinstance(symbol, str)
        and len(symbol) == 1
        and symbol.isupper()
        and symbol != "ε"
    )

def is_terminal(symbol: str) -> bool:
    """Verifica si un símbolo es terminal (minúscula, dígito o ε)."""
    return (
        isinstance(symbol, str)
        and len(symbol) == 1
        and (symbol.islower() or symbol.isdigit())
        and symbol != "ε"
    )

def is_empty_string(symbol: str) -> bool:
    """Verifica si el símbolo representa cadena vacía (ε, epsilon, λ)."""
    return symbol in ("ε", "epsilon", "λ", "")

def is_binary_non_terminal_production(production: list) -> bool:
    """Verifica si una producción es de la forma A → BC (donde B y C son no terminales)."""
    return len(production) == 2 and all(is_non_terminal(sym) for sym in production)

def is_right_linear_production(production: list) -> bool:
    """Verifica si una producción es lineal derecha (A → aB o A → a o A → ε)."""
    if len(production) == 1:
        return is_terminal(production[0]) or is_empty_string(production[0])
    elif len(production) == 2:
        return is_terminal(production[0]) and is_non_terminal(production[1])
    return False


def is_left_linear_production(production: list) -> bool:
    """Verifica si una producción es lineal izquierda (A → Ba o A → a o A → ε)."""
    if len(production) == 1:
        return is_terminal(production[0]) or is_empty_string(production[0])
    elif len(production) == 2:
        return is_non_terminal(production[0]) and is_terminal(production[1])
    return False


def can_derive_empty(symbol: str, productions: dict) -> bool:
    """Verifica si un símbolo puede derivar en cadena vacía."""
    if symbol not in productions:
        return False
    
    # Caso directo: producción vacía (ε)
    if any(is_empty_string(p) for p in productions[symbol]):
        return True
    
    # Caso recursivo: A → B1 B2 ... Bn donde todos los Bi pueden derivar a ε
    for prod in productions[symbol]:
        if all(
            (is_non_terminal(sym) and can_derive_empty(sym, productions))
            or is_empty_string(sym)
            for sym in prod
        ):
            return True
    return False