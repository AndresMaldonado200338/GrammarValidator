from typing import List, Dict, Tuple, Optional, Set
from collections import deque


class StringEvaluator:
    def __init__(self, productions: Dict[str, List[List[str]]], start_symbol: str):
        self.productions = productions
        self.start_symbol = start_symbol
        self.max_derivations = 2000  # Límite para evitar explosión combinatoria
        self.max_length = 100  # Máxima longitud de cadena a derivar

    def belongs_to_grammar(self, input_string: str) -> Tuple[bool, Optional[List[str]]]:
        if len(input_string) > self.max_length:
            return (False, None)
        
        # Primero verificación rápida de símbolos permitidos
        allowed_terminals = set()
        for prods in self.productions.values():
            for prod in prods:
                for symbol in prod:
                    if symbol not in self.productions:  # Es terminal
                        allowed_terminals.add(symbol)
    
        if not all(c in allowed_terminals for c in input_string):
            return (False, None)

        queue = deque()
        queue.append(([self.start_symbol], [f"*{self.start_symbol}*"]))

        visited = set()
        visited.add(self._key([self.start_symbol]))

        derivation_count = 0

        while queue and derivation_count < self.max_derivations:
            current, current_deriv = queue.popleft()
            current_str = ''.join(current)

            if current_str == input_string:
                return (True, current_deriv)

            # Poda: descartar cadenas demasiado largas
            if len(current_str) > len(input_string) * 2:
                continue

            next_char = input_string[len(current_str)] if len(current_str) < len(input_string) else None

            # Buscar todos los no terminales
            for i, symbol in enumerate(current):
                if symbol in self.productions:
                    productions = sorted(
                        self.productions[symbol],
                        key=lambda p: 0 if (p and p[0] == next_char) else 1
                    )
                
                    for production in productions:
                        new_current = current[:i] + production + current[i+1:]
                        new_key = self._key(new_current)
                    
                        if new_key not in visited:
                            visited.add(new_key)
                            new_deriv = current_deriv + [self._format_derivation(new_current)]
                            queue.append((new_current, new_deriv))
                            derivation_count += 1
                
                    break  # Leftmost derivation
    
        return (False, None)

    def _order_productions(self, symbol: str, target: str, current: str, pos: int) -> List[List[str]]:
        """Ordena producciones para probar primero las más probables"""
        productions = self.productions[symbol]

        # Prioridad 1: Producciones que generan el próximo carácter esperado
        next_char = target[len(current[:pos])] if len(
            current[:pos]) < len(target) else None
        prioritized = []
        others = []

        for prod in productions:
            if prod and prod[0] == next_char:
                prioritized.append(prod)
            else:
                others.append(prod)

        return prioritized + others

    def _key(self, symbols: List[str]) -> str:
        """Crea una clave única para memoization"""
        return ''.join(symbols)

    def _format_derivation(self, symbols: List[str]) -> str:
        """Formatea la derivación marcando no terminales con *"""
        return ''.join(f"*{s}*" if s in self.productions else s for s in symbols)
    
    def generate_strings(self, length: int, max_results: int = 50) -> List[str]:
        """Genera cadenas válidas de longitud específica (max 50 por defecto)"""
        if not 1 <= length <= 10:
            raise ValueError("La longitud debe estar entre 1 y 10")

        memo = {}
    
        def generate_from(symbol: str, remaining_length: int) -> List[str]:
            # Verificar cache primero
            key = (symbol, remaining_length)
            if key in memo:
                return memo[key]
    
            # Caso base para terminales
            if symbol not in self.productions:
                return [symbol] if remaining_length == 1 else []
    
            results = []
            for production in self.productions[symbol]:
                # Caso especial para ε (producción vacía)
                if not production:
                    if remaining_length == 0:
                        results.append("")
                    continue
            
                # Calcular el espacio mínimo requerido por esta producción
                min_required = sum(1 for sym in production if sym not in self.productions)
            
                # Si la producción requiere más símbolos de los disponibles, saltar
                if min_required > remaining_length:
                    continue
            
                # Generar recursivamente combinaciones
                def generate_sequence(symbols: List[str], remaining: int) -> List[str]:
                    if not symbols:
                        return [""] if remaining == 0 else []
                
                    first, *rest = symbols
                    seq_results = []
                
                    # Si el símbolo es terminal, debe consumir exactamente 1 de longitud
                    if first not in self.productions:
                        if remaining >= 1:
                            for suffix in generate_sequence(rest, remaining - 1):
                                seq_results.append(first + suffix)
                    else:
                        # Si es no terminal, probar todas las longitudes posibles
                        for l in range(0, remaining - len(rest) + 1):
                            for prefix in generate_from(first, l):
                                for suffix in generate_sequence(rest, remaining - l):
                                    seq_results.append(prefix + suffix)
                
                    return seq_results
            
                results.extend(generate_sequence(production, remaining_length))
        
            # Almacenar en cache y devolver
            memo[key] = results
            return results

        # Generar resultados y limitar
        results = generate_from(self.start_symbol, length)
        return sorted(list(set(results)))[:max_results]