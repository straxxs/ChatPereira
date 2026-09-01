from functools import wraps
from flask import Blueprint, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
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


def page_login_required(roles=None):
    roles = set(roles or [])
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("login_page"))
            if roles and session.get("rol") not in roles:
                return redirect(url_for("index"))
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

    if not user:
        return jsonify({"ok": False, "mensaje": "Credenciales inválidas."}), 401

    stored_password = user["contraseña"] or ""
    password_ok = False

    # Compatibilidad con los datos de prueba antiguos. Si la base todavía
    # contiene una contraseña en texto plano, se valida una vez y se migra
    # inmediatamente a un hash de Werkzeug. Los nuevos registros siempre
    # se guardan hasheados desde registro.py.
    if stored_password.startswith(("scrypt:", "pbkdf2:")):
        try:
            password_ok = check_password_hash(stored_password, password)
        except ValueError:
            password_ok = False
    elif stored_password == password:
        password_ok = True
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE USUARIO SET contraseña=%s WHERE id_usuario=%s",
                    (generate_password_hash(password), user["id_usuario"]),
                )
        finally:
            conn.close()

    if not password_ok:
        return jsonify({"ok": False, "mensaje": "Credenciales inválidas."}), 401

    rol = detectar_rol(user["id_usuario"])
    if not rol:
        return jsonify({"ok": False, "mensaje": "La cuenta no tiene un rol válido."}), 403

    session.clear()
    session["user_id"] = user["id_usuario"]
    session["rol"] = rol
    session["nombre_usuario"] = user["nombre_usuario"]
    session["apellido_usuario"] = user["apellido_usuario"]
    session["mail"] = user["mail"]

    return jsonify({
        "ok": True,
        "usuario": {
            "id_usuario": user["id_usuario"],
            "nombre_usuario": user["nombre_usuario"],
            "apellido_usuario": user["apellido_usuario"],
            "mail": user["mail"],
        },
        "rol": rol,
    })


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
