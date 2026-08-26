from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from db import get_connection

registro_bp = Blueprint("registro", __name__)


@registro_bp.post("/paciente")
def registrar_paciente():
    data = request.get_json(silent=True) or {}
    requeridos = ["nombre_usuario", "apellido_usuario", "mail", "DNI", "password", "sexo", "edad"]
    if any(not data.get(campo) for campo in requeridos):
        return jsonify({"ok": False, "mensaje": "Faltan datos obligatorios."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO USUARIO
                (nombre_usuario, apellido_usuario, mail, DNI, contraseña)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["nombre_usuario"], data["apellido_usuario"], data["mail"],
                data["DNI"], generate_password_hash(data["password"]),
            ))
            user_id = cur.lastrowid
            cur.execute("""
                INSERT INTO PACIENTE
                (id_paciente, sexo, edad, telefono, historial_salud)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user_id, data["sexo"], data["edad"],
                data.get("telefono"), data.get("historial_salud"),
            ))
            return jsonify({"ok": True, "id_usuario": user_id}), 201
    finally:
        conn.close()
