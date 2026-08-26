from flask import Blueprint, jsonify
from db import get_connection
from modules.auth import login_required

medicos_bp = Blueprint("medicos", __name__)


@medicos_bp.get("")
def listar_medicos():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT m.id_medico, u.nombre_usuario, u.apellido_usuario,
                       m.horarios_atencion, m.telefono,
                       e.id_especialidad, e.nombre AS especialidad
                FROM MEDICO m
                JOIN USUARIO u ON u.id_usuario = m.id_medico
                JOIN ESPECIALIDAD e ON e.id_especialidad = m.id_especialidad
                ORDER BY u.apellido_usuario, u.nombre_usuario
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@medicos_bp.get("/mis-consultas")
@login_required(["medico"])
def mis_consultas():
    return {"ok": True, "mensaje": "Usar /consultas/pendientes para la bandeja de consultas."}
