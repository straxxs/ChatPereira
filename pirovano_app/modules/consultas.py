from flask import Blueprint, request, jsonify, session
from db import get_connection
from modules.auth import login_required

consultas_bp = Blueprint("consultas", __name__)


@consultas_bp.post("")
@login_required(["paciente"])
def crear_consulta():
    data = request.get_json(silent=True) or {}
    descripcion = data.get("descripcion_sintomas")
    id_medico = data.get("id_medico")
    if not descripcion or not id_medico:
        return jsonify({"ok": False, "mensaje": "Faltan datos obligatorios."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO CONSULTA
                   (descripcion_sintomas, fecha_hora, id_medico, id_paciente)
                   VALUES (%s, NOW(), %s, %s)""",
                (descripcion, id_medico, session["user_id"]),
            )
            return jsonify({"ok": True, "id_consulta": cur.lastrowid}), 201
    finally:
        conn.close()


@consultas_bp.get("/mis-consultas")
@login_required(["paciente"])
def mis_consultas():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM CONSULTA WHERE id_paciente=%s ORDER BY fecha_hora DESC",
                (session["user_id"],),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@consultas_bp.get("/pendientes")
@login_required(["medico"])
def pendientes():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM CONSULTA WHERE id_medico=%s AND estado IN ('Pendiente','En Revision') ORDER BY fecha_hora ASC",
                (session["user_id"],),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()
