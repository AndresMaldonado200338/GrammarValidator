from flask import Flask, render_template, request, jsonify
import validators.hierarchy_validator as hierarchy_validator

app = Flask(__name__)

# Función para procesar las reglas de producción ingresadas en el formulario
def obtener_producciones(entrada):
    """
    Convierte la entrada del formulario en un diccionario de producciones.

    Argumento:
    entrada: Lista de strings con las reglas de producción.

    Retorno:
    Diccionario donde las claves son las partes izquierdas y los valores son listas de producciones.
    """
    producciones = {}

    for linea in entrada:
        partes = linea.split("->")
        if len(partes) != 2:
            continue

        izquierda = partes[0].strip()
        derechas = [p.strip() for p in partes[1].split("|")]

        if izquierda in producciones:
            producciones[izquierda].extend(derechas)
        else:
            producciones[izquierda] = derechas

    return producciones

# Función para extraer no terminales, terminales y axioma inicial
def obtener_simbolos(productions):
    """
    Extrae los no terminales, terminales y el axioma inicial de las reglas de producción.

    Argumento:
    productions: Diccionario donde las claves son los no terminales y los valores son listas de producciones.

    Retorno:
    Un diccionario con los conjuntos de no terminales, terminales y el axioma inicial.
    """
    no_terminales = set(
        productions.keys())
    terminales = set()

    for left, rights in productions.items():
        for right in rights:
            for simbolo in right:
                if simbolo.isupper():
                    no_terminales.add(simbolo)
                elif simbolo.islower():
                    terminales.add(simbolo)

    axioma_inicial = next(iter(productions.keys())) if productions else None

    return {"no_terminales": sorted(no_terminales), "terminales": sorted(terminales), "axioma": axioma_inicial}


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/validate_grammar", methods=["POST"])
def validate_grammar():
    data = request.json
    reglas = data.get("P", [])

    if not reglas:
        return jsonify({"error": "No se ingresaron reglas de producción"}), 400

    productions = obtener_producciones(reglas)
    simbolos = obtener_simbolos(productions)

    tipo = "no es de Tipo 2 ni Tipo 3"

    if hierarchy_validator.is_type3(productions):
        tipo = "es de tipo 3 (Gramática Regular)"
    elif hierarchy_validator.is_type2(productions):
        tipo = "es de tipo 2 (Libre de Contexto)"

    resultado = {
        "no_terminales": simbolos["no_terminales"],
        "terminales": simbolos["terminales"],
        "axioma": simbolos["axioma"],
        "tipo": tipo
    }

    return jsonify(resultado)


@app.route('/validate_string', methods=['POST'])
def validate_string():
    data = request.json
    cadena = data.get("cadena", "")

    if not cadena:
        return jsonify({"error": "No se ingresó ninguna cadena"}), 400
    return jsonify({"result": "Cadena válida", "derivation_tree": "Árbol de derivación"})


if __name__ == '__main__':
    app.run(debug=True)
