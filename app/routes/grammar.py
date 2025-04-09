import logging
from flask import Blueprint, request, jsonify, render_template
from app.services.parser import parse_grammar
from app.services.evaluator import evaluate_grammar
from app.services.string_evaluator import StringEvaluator

#Que muestre info tambien, no solo error
logging.basicConfig(level=logging.ERROR)
logging.getLogger().setLevel(logging.INFO)

# Blueprint para las rutas de gramática
grammar_bp = Blueprint("grammar", __name__)

@grammar_bp.route("/")
def index():
    """Ruta principal para renderizar la página de inicio."""
    return render_template("index.html")

@grammar_bp.route("/evaluate", methods=["POST"])
def evaluate_grammar_route():
    """Endpoint para evaluar gramáticas y cadenas de entrada."""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data:
            return jsonify({"error": "No se recibieron datos JSON"}), 400
        
        required_fields = ["grammar_text", "input_string"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido faltante: {field}"}), 400

        grammar_text = data["grammar_text"]
        input_string = data["input_string"]

        # Parsear gramática
        no_terminals, terminals, initial_axiom, productions = parse_grammar(grammar_text)

        # Imprimir datos que llegaron
        logging.info(f"Gramática: {grammar_text}")
        logging.info(f"Cadena de entrada: {input_string}")
        logging.info(f"No terminales: {no_terminals}")
        logging.info(f"Terminales: {terminals}")
        logging.info(f"Axioma inicial: {initial_axiom}")
        logging.info(f"Producciones: {productions}")

        # Evaluar tipo de gramática
        grammar_type = evaluate_grammar(productions)
        
        # Evaluar cadena
        evaluator = StringEvaluator(productions, initial_axiom)
        belongs, derivations = evaluator.belongs_to_grammar(input_string)
        
        # Formatear derivaciones con flechas si existen
        formatted_derivations = None
        if derivations:
            formatted_derivations = " → ".join(derivations)

        logging.info(f"derivaciones: {derivations}")
        
        return jsonify({
            'grammar_type': grammar_type,
            'belongs_to_grammar': belongs,
            'derivation': formatted_derivations,
            'message': f'Gramática {grammar_type}. Cadena: {"aceptada" if belongs else "rechazada"}'
        })

    except RecursionError:
        return jsonify({
            'error': 'La gramática causa recursión infinita',
            'solution': 'Revisa producciones recursivas izquierdas como A → Aa',
            'grammar_type': evaluate_grammar(productions) if 'productions' in locals() else None
        }), 400
        
    except ValueError as e:
        logging.error(f'Error de validación: {str(e)}')
        return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        logging.error(f'Error interno: {str(e)}', exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500

@grammar_bp.route("/check", methods=["POST"])
def check_grammar_type_route():
    """Endpoint solo para verificar el tipo de gramática."""
    try:
        data = request.get_json()
        
        if not data or "grammar_text" not in data:
            return jsonify({"error": "Se requiere el campo 'grammar_text'"}), 400

        _, _, _, productions = parse_grammar(data["grammar_text"])
        grammar_type = evaluate_grammar(productions)
        
        return jsonify({
            "grammar_type": grammar_type
        })

    except Exception as e:
        logging.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 400
    
@grammar_bp.route("/generate-strings", methods=["POST"])
def generate_strings():
    """Endpoint para generar cadenas válidas de longitud X"""
    try:
        data = request.get_json()
        
        if not data or "grammar_text" not in data or "length" not in data:
            return jsonify({"error": "Se requieren grammar_text y length"}), 400
        
        length = int(data["length"])
        if not 1 <= length <= 10:
            return jsonify({"error": "La longitud debe estar entre 1 y 10"}), 400

        # Parsear gramática
        _, _, initial_axiom, productions = parse_grammar(data["grammar_text"])
        
        # Generar cadenas
        evaluator = StringEvaluator(productions, initial_axiom)
        generated_strings = evaluator.generate_strings(length)

        # Imprimir datos que llegaron
        logging.info(f"longitud: {length}")
        logging.info(f"gramatica: {data['grammar_text']}")
        logging.info(f"cadenas generadas: {generated_strings}")
        
        return jsonify({
            'generated_strings': generated_strings,
            'count': len(generated_strings),
            'note': 'Showing first 50 results' if len(generated_strings) == 50 else ''
        })

    except Exception as e:
        logging.error(f'Error: {str(e)}', exc_info=True)
        return jsonify({'error': str(e)}), 400