import os
from flask import Flask

def create_app():
    # Obtener rutas absolutas
    base_path = os.path.abspath(os.path.dirname(__file__))
    template_path = os.path.abspath(os.path.join(base_path, "../templates"))
    static_path = os.path.abspath(os.path.join(base_path, "../static"))

    # Crear la aplicación Flask
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    # Importar y registrar el blueprint correctamente
    from app.routes import grammar_bp
    app.register_blueprint(grammar_bp, url_prefix="/")

    return app

__all__ = ["create_app"]
