from flask import Flask, jsonify
from config import Config
from modules.auth import auth_bp
from modules.consultas import consultas_bp
from modules.medicos import medicos_bp
from modules.pacientes import pacientes_bp
from modules.recetas import recetas_bp
from modules.admin import admin_bp
from modules.especialidades import especialidades_bp
from modules.devoluciones import devoluciones_bp
from modules.registro import registro_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(consultas_bp, url_prefix="/consultas")
    app.register_blueprint(medicos_bp, url_prefix="/medicos")
    app.register_blueprint(pacientes_bp, url_prefix="/pacientes")
    app.register_blueprint(recetas_bp, url_prefix="/recetas")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(especialidades_bp, url_prefix="/especialidades")
    app.register_blueprint(devoluciones_bp, url_prefix="/devoluciones")
    app.register_blueprint(registro_bp, url_prefix="/registro")

    @app.get("/")
    def index():
        return jsonify({"sistema": "Instituto Pirovano", "estado": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
