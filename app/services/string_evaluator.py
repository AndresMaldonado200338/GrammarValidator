from .utils import is_non_terminal, is_terminal, is_empty_string

class StringEvaluator:
    def __init__(self, productions: dict, start_symbol: str):
        self.productions = productions
        self.start_symbol = start_symbol
        self.derivation_history = []
        self.max_recursion_depth = 1000  # Límite seguro para recursión

    def belongs_to_grammar(self, input_string: str) -> bool:
        """Determina si la cadena pertenece a la gramática."""
        self.derivation_history = [self._format_step(self.start_symbol)]
        
        if not input_string:  # Manejo de cadena vacía
            return any(is_empty_string(p) for p in self.productions.get(self.start_symbol, []))

        result = self._check_type_3(input_string) if self._is_type_3() else self._check_type_2(input_string, depth=0)
        
        # Convertir historial a formato de flechas
        self.derivation_history = " → ".join(self.derivation_history)
        return result

    def _is_type_3(self) -> bool:
        """Verifica si es gramática tipo 3 (regular)."""
        has_right = True
        has_left = True
        
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                if len(rhs) == 1:
                    if not (is_terminal(rhs[0]) or is_empty_string(rhs[0])):
                        return False
                elif len(rhs) == 2:
                    if not (is_terminal(rhs[0]) and is_non_terminal(rhs[1])):
                        has_right = False
                    if not (is_non_terminal(rhs[0]) and is_terminal(rhs[1])):
                        has_left = False
                    if not has_right and not has_left:
                        return False
                else:
                    return False
        return has_right or has_left

    def _check_type_3(self, input_string: str) -> bool:
        """Autómata para gramáticas regulares (lineales derechas o izquierdas)."""
        if self._is_left_linear():
            return self._check_left_linear(input_string)
        return self._check_right_linear(input_string)
        
    def _is_left_linear(self) -> bool:
        """Determina si la gramática es lineal izquierda."""
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                if len(rhs) == 2 and is_non_terminal(rhs[0]) and is_terminal(rhs[1]):
                    return True
        return False
    
    def _check_right_linear(self, input_string: str) -> bool:
        """Procesa gramáticas lineales derechas (A → aB)."""
        current_deriv = self.start_symbol
        remaining = input_string

        while remaining:
            found = False
            # Buscar el primer no terminal de izquierda a derecha
            for i, symbol in enumerate(current_deriv):
                if is_non_terminal(symbol):
                    for rhs in self.productions.get(symbol, []):
                        if len(rhs) == 1 and rhs[0] == remaining:
                            new_deriv = current_deriv[:i] + rhs[0] + current_deriv[i+1:]
                            self.derivation_history.append(self._format_step(new_deriv))
                            return True
                        if (len(rhs) == 2 and remaining and 
                            rhs[0] == remaining[0] and is_non_terminal(rhs[1])):
                            new_deriv = current_deriv[:i] + rhs[0] + rhs[1] + current_deriv[i+1:]
                            self.derivation_history.append(self._format_step(new_deriv))
                            current_deriv = new_deriv
                            remaining = remaining[1:]
                            found = True
                            break
                    if found:
                        break
            if not found:
                break

        if not remaining:
            return True
        return False
    
    def _check_left_linear(self, input_string: str) -> bool:
        """Procesa gramáticas lineales izquierdas (A → Ba)."""
        def parse(derivation: str, remaining: str) -> bool:
            if not remaining:
                return True

            # Buscar el último no terminal de derecha a izquierda
            for i in range(len(derivation)-1, -1, -1):
                symbol = derivation[i]
                if is_non_terminal(symbol):
                    for rhs in self.productions.get(symbol, []):
                        if len(rhs) == 1 and rhs[0] == remaining:
                            new_deriv = derivation[:i] + rhs[0] + derivation[i+1:]
                            self.derivation_history.append(self._format_step(new_deriv))
                            return True
                        if (len(rhs) == 2 and is_non_terminal(rhs[0]) and 
                            is_terminal(rhs[1]) and remaining.endswith(rhs[1])):
                            new_deriv = derivation[:i] + rhs[0] + rhs[1] + derivation[i+1:]
                            self.derivation_history.append(self._format_step(new_deriv))
                            if parse(new_deriv, remaining[:-1]):
                                return True
                            self.derivation_history.pop()  # Backtrack
                    break  # Solo procesamos el último NT
            return False

        return parse(self.start_symbol, input_string)

    def _check_type_2(self, input_string: str, depth: int) -> bool:
        """Parsing para gramáticas libres de contexto con control de profundidad."""
        if depth > self.max_recursion_depth:
            raise RecursionError("Profundidad de recursión excedida")
        
        def parse(symbol: str, remaining: str, depth: int) -> bool:
            if depth > self.max_recursion_depth:
                return False
                
            for rhs in self.productions.get(symbol, []):
                if not rhs:  # Producción ε
                    if not remaining:
                        self.derivation_history.append(self._format_step("ε"))
                        return True
                    continue
                
                if (len(rhs) == 2 and is_non_terminal(rhs[0]) and 
                    is_terminal(rhs[1]) and remaining.endswith(rhs[1])):
                    new_deriv = remaining[:-1] + rhs[0] + rhs[1]
                    self.derivation_history.append(self._format_step(new_deriv))
                    if parse(rhs[0], remaining[:-1], depth + 1):
                        return True
                    self.derivation_history.pop()
                
                if parse_sequence(rhs, remaining, depth + 1):
                    return True
                    
            return False

        def parse_sequence(sequence: list, remaining: str, depth: int) -> bool:
            if not sequence:
                return not remaining
                
            first, *rest = sequence
            
            if is_terminal(first):
                if remaining and remaining[0] == first:
                    return parse_sequence(rest, remaining[1:], depth + 1)
                return False
            else:
                return parse(first, remaining, depth + 1)

        return parse(self.start_symbol, input_string, depth)

    def _format_step(self, step: str) -> str:
        """Formatea un paso de derivación resaltando no terminales con *"""
        formatted = []
        for char in step:
            if is_non_terminal(char):
                formatted.append(f"*{char}*")
            else:
                formatted.append(char)
        return "".join(formatted)