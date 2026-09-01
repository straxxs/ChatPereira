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
    medicamentos = (data.get("medicamentos") or "").strip() or None
    indicaciones_receta = (data.get("indicaciones_receta") or "").strip() or None
    archivo = request.files.get("imagen")

    if not descripcion and not archivo and not turno and not medicamentos:
        return jsonify({"ok": False, "mensaje": "La respuesta necesita texto, imagen, turno o receta."}), 400

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

            cur.execute(
                """INSERT INTO DEVOLUCION
                   (turno, descripcion, fecha_hora_devolucion, id_consulta)
                   VALUES (%s, %s, NOW(), %s)""",
                (turno, descripcion or "(Sin texto)", id_consulta),
            )
            id_devolucion = cur.lastrowid

            id_receta = None
            if medicamentos:
                cur.execute(
                    "SELECT telefono FROM PACIENTE WHERE id_paciente=%s",
                    (consulta["id_paciente"],),
                )
                paciente = cur.fetchone()
                telefono_paciente = paciente["telefono"] if paciente else None

                cur.execute(
                    """INSERT INTO RECETA (medicamentos, telefono, descripcion)
                       VALUES (%s, %s, %s)""",
                    (medicamentos, telefono_paciente, indicaciones_receta),
                )
                id_receta = cur.lastrowid
                cur.execute(
                    "INSERT INTO DETALLE_DEVOLUCION (id_devolucion, id_receta) VALUES (%s, %s)",
                    (id_devolucion, id_receta),
                )

            image_name = None
            if archivo and archivo.filename:
                from modules.consultas import upload_chat_image
                image_name, image_error = upload_chat_image(archivo)
                if image_error:
                    return jsonify({"ok": False, "mensaje": image_error}), 400

            contenido_mensaje = descripcion or None
            if turno:
                texto_turno = f"📅 Turno propuesto: {turno}"
                contenido_mensaje = f"{contenido_mensaje}\n\n{texto_turno}" if contenido_mensaje else texto_turno
            if medicamentos:
                texto_receta = f"💊 Receta #{id_receta}: {medicamentos}"
                if indicaciones_receta:
                    texto_receta += f"\nIndicaciones: {indicaciones_receta}"
                contenido_mensaje = f"{contenido_mensaje}\n\n{texto_receta}" if contenido_mensaje else texto_receta

            cur.execute(
                """INSERT INTO MENSAJE
                   (id_consulta, id_usuario, tipo, contenido, imagen, fecha_hora)
                   VALUES (%s, %s, 'medico', %s, %s, NOW())""",
                (id_consulta, session["user_id"], contenido_mensaje, image_name),
            )

            conn.commit()
            return jsonify({"ok": True, "id_devolucion": id_devolucion, "id_receta": id_receta}), 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@devoluciones_bp.post("/<int:id_consulta>/finalizar")
@login_required(["medico"])
def finalizar_consulta(id_consulta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_consulta FROM CONSULTA WHERE id_consulta=%s AND id_medico=%s",
                (id_consulta, session["user_id"]),
            )
            if not cur.fetchone():
                return jsonify({"ok": False, "mensaje": "Consulta inexistente o no asignada."}), 404
            cur.execute(
                "UPDATE CONSULTA SET estado='Finalizada' WHERE id_consulta=%s",
                (id_consulta,),
            )
            return jsonify({"ok": True})
    finally:
        conn.close()