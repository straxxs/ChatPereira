from flask import Blueprint, request, jsonify, session
from db import get_connection
from modules.auth import login_required


devoluciones_bp = Blueprint("devoluciones", __name__)


@devoluciones_bp.post("/<int:id_consulta>")
@login_required(["medico"])
def responder_consulta(id_consulta):
    data = request.form if request.form else (request.get_json(silent=True) or {})
    descripcion = (data.get("descripcion") or "").strip()
    turno = data.get("turno") or None
    id_receta = data.get("id_receta") or None
    archivo = request.files.get("imagen")

    if not descripcion and not archivo:
        return jsonify({"ok": False, "mensaje": "La respuesta necesita un texto o una imagen."}), 400

    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_consulta, id_paciente FROM CONSULTA WHERE id_consulta=%s AND id_medico=%s",
                (id_consulta, session["user_id"]),
            )
            consulta = cur.fetchone()
            if not consulta:
                return jsonify({"ok": False, "mensaje": "Consulta inexistente o no asignada."}), 404

            # La devolución sigue siendo la operación principal del médico.
            # El trigger actualizar_estado_consulta cambia el estado a Respondida
            # y el trigger registrar_cambio_estado genera el historial.
            cur.execute(
                """INSERT INTO DEVOLUCION
                   (turno, descripcion, fecha_hora_devolucion, id_consulta)
                   VALUES (%s, %s, NOW(), %s)""",
                (turno, descripcion or "(Imagen adjunta)", id_consulta),
            )
            id_devolucion = cur.lastrowid

            if id_receta:
                cur.execute(
                    "INSERT INTO DETALLE_DEVOLUCION (id_devolucion, id_receta) VALUES (%s, %s)",
                    (id_devolucion, id_receta),
                )

            # Para imágenes, reutilizamos el almacenamiento del módulo de consultas.
            image_name = None
            if archivo and archivo.filename:
                from modules.consultas import upload_chat_image
                image_name, image_error = upload_chat_image(archivo)
                if image_error:
                    return jsonify({"ok": False, "mensaje": image_error}), 400

            cur.execute(
                """INSERT INTO MENSAJE
                   (id_consulta, id_usuario, tipo, contenido, imagen, fecha_hora)
                   VALUES (%s, %s, 'medico', %s, %s, NOW())""",
                (id_consulta, session["user_id"], descripcion or None, image_name),
            )

            conn.commit()
            return jsonify({"ok": True, "id_devolucion": id_devolucion}), 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
