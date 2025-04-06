from .utils import (
    is_non_terminal,
    is_terminal,
    is_empty_string,
    is_right_linear_production,
    is_left_linear_production,
)

def is_type_3(productions: dict) -> bool:
    """Determina si la gramática es tipo 3 (regular)."""
    has_right_linear = True
    has_left_linear = True

    for lhs, rhs_list in productions.items():
        for rhs in rhs_list:
            if not is_right_linear_production(rhs):
                has_right_linear = False
            if not is_left_linear_production(rhs):
                has_left_linear = False
            if not has_right_linear and not has_left_linear:
                return False  # No cumple ninguna linealidad

    return has_right_linear or has_left_linear

def is_type_2(productions: dict) -> bool:
    """Determina si la gramática es tipo 2 (libre de contexto)."""
    for lhs, rhs_list in productions.items():
        if not is_non_terminal(lhs):
            return False  # LHS debe ser un no terminal
        
        for rhs in rhs_list:
            for symbol in rhs:
                if not (is_non_terminal(symbol) or is_terminal(symbol) or is_empty_string(symbol)):
                    return False  # Símbolo inválido en RHS
    return True

def evaluate_grammar(productions: dict) -> str:
    """Evalúa la gramática y devuelve su tipo según Chomsky."""
    if is_type_3(productions):
        return "Tipo 3 (Regular)"
    elif is_type_2(productions):
        return "Tipo 2 (Libre de contexto)"
    else:
        return "No es tipo 2 ni 3"