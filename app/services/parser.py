def parse_grammar(grammar_text):
    """Parsea el texto de la gramática en formato N, T, S, P."""
    no_terminals = set()
    terminals = set()
    initial_axiom = ""
    productions = {}

    lines = [line.strip() for line in grammar_text.split("\n") if line.strip()]

    # Extraer N, T, S
    try:
        no_terminals = set(next(line.split("=")[1].strip() for line in lines if line.startswith("N =")).split())
        terminals = set(next(line.split("=")[1].strip() for line in lines if line.startswith("T =")).split())
        initial_axiom = next(line.split("=")[1].strip() for line in lines if line.startswith("S ="))
    except StopIteration:
        raise ValueError("El formato de la gramática es incorrecto. Faltan secciones N, T o S.")

    # Procesar producciones (P = { ... })
    in_productions = False
    for line in lines:
        line = line.split("#")[0].strip()  # Eliminar comentarios
        if line.startswith("P = {"):
            in_productions = True
            continue
        if line == "}" and in_productions:
            in_productions = False
            break
        if in_productions and "→" in line:
            lhs, rhs = line.split("→", 1)
            lhs = lhs.strip()
            rhs = rhs.strip()

            # Validar que el lhs esté en no_terminals
            if lhs not in no_terminals:
                raise ValueError(f"LHS '{lhs}' no está en los no terminales definidos.")
            
            # Manejar múltiples alternativas separadas por |
            alternatives = [alt.strip() for alt in rhs.split("|")] if "|" in rhs else [rhs]

            for alt in alternatives:
                if alt in ("ε", "epsilon", "λ"):
                    productions.setdefault(lhs, []).append([])
                    continue

                symbols = []
                current = ""
                i = 0
                while i < len(alt):
                    if alt[i] == " ":
                        if current:
                            symbols.append(current)
                            current = ""
                        i += 1
                    else:
                        found = False
                        for nt in no_terminals:
                            if alt.startswith(nt, i):
                                if current:
                                    symbols.append(current)
                                    current = ""
                                symbols.append(nt)
                                i += len(nt)
                                found = True
                                break
                        if not found:
                            current += alt[i]
                            i += 1
                if current:
                    symbols.append(current)

                for symbol in symbols:
                    if symbol not in no_terminals and symbol not in terminals:
                        raise ValueError(f"Símbolo '{symbol}' no está definido como terminal o no terminal.")

                productions.setdefault(lhs, []).append(symbols)

    return no_terminals, terminals, initial_axiom, productions