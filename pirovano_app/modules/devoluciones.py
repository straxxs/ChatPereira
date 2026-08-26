from flask import Blueprint, request, jsonify, session
from db import get_connection
from modules.auth import login_required

devoluciones_bp = Blueprint("devoluciones", __name__)


@devoluciones_bp.post("/<int:id_consulta>")
@login_required(["medico"])
def responder_consulta(id_consulta):
    data = request.get_json(silent=True) or {}
    descripcion = data.get("descripcion")
    turno = data.get("turno")
    id_receta = data.get("id_receta")

    if not descripcion:
        return jsonify({"ok": False, "mensaje": "La respuesta es obligatoria."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_consulta FROM CONSULTA WHERE id_consulta=%s AND id_medico=%s",
                (id_consulta, session["user_id"]),
            )
            consulta = cur.fetchone()
            if not consulta:
                return jsonify({"ok": False, "mensaje": "Consulta inexistente o no asignada."}), 404

            cur.execute(
                "INSERT INTO DEVOLUCION (turno, descripcion, fecha_hora_devolucion, id_consulta) VALUES (%s, %s, NOW(), %s)",
                (turno, descripcion, id_consulta),
            )
            id_devolucion = cur.lastrowid

            if id_receta:
                cur.execute(
                    "INSERT INTO DETALLE_DEVOLUCION (id_devolucion, id_receta) VALUES (%s, %s)",
                    (id_devolucion, id_receta),
                )

            return jsonify({"ok": True, "id_devolucion": id_devolucion}), 201
    finally:
        conn.close()
