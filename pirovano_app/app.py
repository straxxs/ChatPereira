from flask import Flask, render_template, session, redirect, url_for
from config import Config
from modules.auth import auth_bp, page_login_required
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
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        if session.get("user_id"):
            destino = {
                "paciente": "paciente_dashboard",
                "medico": "medico_dashboard",
                "admin": "admin_dashboard",
            }.get(session.get("rol"))
            if destino:
                return redirect(url_for(destino))
        return render_template("login.html")

    @app.get("/registro")
    def registro_page():
        if session.get("user_id"):
            return redirect(url_for("index"))
        return render_template("registro.html")

    @app.get("/paciente-dashboard")
    @page_login_required(["paciente"])
    def paciente_dashboard():
        return render_template("paciente_dashboard.html")

    @app.get("/medico-dashboard")
    @page_login_required(["medico"])
    def medico_dashboard():
        return render_template("medico_dashboard.html")

    @app.get("/admin-dashboard")
    @page_login_required(["admin"])
    def admin_dashboard():
        return render_template("admin_dashboard.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
