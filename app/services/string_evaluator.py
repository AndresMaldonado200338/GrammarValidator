from typing import List, Dict, Tuple, Optional, Set
from collections import deque

class StringEvaluator:
    def __init__(self, productions: Dict[str, List[List[str]]], start_symbol: str):
        self.productions = productions
        self.start_symbol = start_symbol
        self.max_derivations = 1000  # Límite para evitar explosión combinatoria
        self.max_length = 30  # Máxima longitud de cadena a derivar

    def belongs_to_grammar(self, input_string: str) -> Tuple[bool, Optional[List[str]]]:
        """Versión optimizada con BFS y poda temprana"""
        if len(input_string) > self.max_length:
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
                
            if len(current_str) > len(input_string) * 2:  # Poda: descartar cadenas demasiado largas
                continue
                
            # Buscar todos los no terminales
            for i, symbol in enumerate(current):
                if symbol in self.productions:
                    # Ordenar producciones para probar primero las más prometedoras
                    ordered_productions = self._order_productions(symbol, input_string, current_str, i)
                    
                    for production in ordered_productions:
                        new_current = current[:i] + production + current[i+1:]
                        new_key = self._key(new_current)
                        
                        if new_key not in visited:
                            visited.add(new_key)
                            new_deriv = current_deriv + [self._format_derivation(new_current)]
                            queue.append((new_current, new_deriv))
                            derivation_count += 1
                    
                    break  # Solo expandir el primer no terminal (estrategia leftmost)
                    
        return (False, None)

    def _order_productions(self, symbol: str, target: str, current: str, pos: int) -> List[List[str]]:
        """Ordena producciones para probar primero las más probables"""
        productions = self.productions[symbol]
        
        # Prioridad 1: Producciones que generan el próximo carácter esperado
        next_char = target[len(current[:pos])] if len(current[:pos]) < len(target) else None
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