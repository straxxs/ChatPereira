from flask import Blueprint, request, jsonify
from db import get_connection
from modules.auth import login_required

recetas_bp = Blueprint("recetas", __name__)


@recetas_bp.post("")
@login_required(["medico"])
def crear_receta():
    data = request.get_json(silent=True) or {}
    medicamentos = data.get("medicamentos")
    descripcion = data.get("descripcion")
    if not medicamentos:
        return jsonify({"ok": False, "mensaje": "Debe indicar al menos un medicamento."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO RECETA (medicamentos, descripcion) VALUES (%s, %s)",
                (medicamentos, descripcion),
            )
            return jsonify({"ok": True, "id_receta": cur.lastrowid}), 201
    finally:
        conn.close()
