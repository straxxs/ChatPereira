from flask import Blueprint, request, jsonify
from db import get_connection
from modules.auth import login_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/usuarios")
@login_required(["admin"])
def listar_usuarios():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id_usuario, nombre_usuario, apellido_usuario, mail, DNI
                FROM USUARIO ORDER BY id_usuario
            """)
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@admin_bp.delete("/usuarios/<int:user_id>")
@login_required(["admin"])
def eliminar_usuario(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM USUARIO WHERE id_usuario=%s", (user_id,))
            if cur.rowcount == 0:
                return jsonify({"ok": False, "mensaje": "Usuario inexistente."}), 404
            return jsonify({"ok": True, "mensaje": "Usuario eliminado."})
    finally:
        conn.close()
