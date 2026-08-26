from flask import Blueprint, jsonify, session
from db import get_connection
from modules.auth import login_required

pacientes_bp = Blueprint("pacientes", __name__)


@pacientes_bp.get("/perfil")
@login_required(["paciente"])
def perfil():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.nombre_usuario, u.apellido_usuario,
                       u.mail, u.DNI, p.sexo, p.edad, p.telefono,
                       p.historial_salud
                FROM USUARIO u
                JOIN PACIENTE p ON p.id_paciente = u.id_usuario
                WHERE u.id_usuario=%s
            """, (session["user_id"],))
            paciente = cur.fetchone()
    finally:
        conn.close()
    return jsonify(paciente or {})
