from functools import wraps
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from db import get_connection

auth_bp = Blueprint("auth", __name__)


def login_required(roles=None):
    roles = set(roles or [])
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"ok": False, "mensaje": "Debe iniciar sesión."}), 401
            if roles and session.get("rol") not in roles:
                return jsonify({"ok": False, "mensaje": "No tiene permisos."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    mail = data.get("mail")
    password = data.get("password")
    if not mail or not password:
        return jsonify({"ok": False, "mensaje": "Mail y contraseña son obligatorios."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM USUARIO WHERE mail = %s", (mail,))
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["contraseña"], password):
        return jsonify({"ok": False, "mensaje": "Credenciales inválidas."}), 401

    session["user_id"] = user["id_usuario"]
    session["rol"] = detectar_rol(user["id_usuario"])
    return jsonify({"ok": True, "usuario": user, "rol": session["rol"]})


def detectar_rol(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM ADMINISTRADOR WHERE id_usuario=%s", (user_id,))
            if cur.fetchone(): return "admin"
            cur.execute("SELECT 1 FROM MEDICO WHERE id_medico=%s", (user_id,))
            if cur.fetchone(): return "medico"
            cur.execute("SELECT 1 FROM PACIENTE WHERE id_paciente=%s", (user_id,))
            if cur.fetchone(): return "paciente"
    finally:
        conn.close()
    return None


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True, "mensaje": "Sesión cerrada."})
