import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app, send_from_directory
from werkzeug.utils import secure_filename
from db import get_connection
from modules.auth import login_required

consultas_bp = Blueprint("consultas", __name__)
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_image(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def upload_chat_image(file):
    if not file or not file.filename:
        return None, None
    if not allowed_image(file.filename):
        return None, "Formato de imagen no permitido. Usá JPG, PNG, WEBP o GIF."

    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "chat")
    os.makedirs(upload_dir, exist_ok=True)
    extension = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(os.path.join(upload_dir, filename))
    return filename, None


def user_can_access_consulta(cur, id_consulta):
    cur.execute(
        """SELECT c.id_consulta, c.id_paciente, c.id_medico
           FROM CONSULTA c
           WHERE c.id_consulta=%s""",
        (id_consulta,),
    )
    consulta = cur.fetchone()
    if not consulta:
        return None
    if session.get("rol") == "paciente" and consulta["id_paciente"] != session["user_id"]:
        return None
    if session.get("rol") == "medico" and consulta["id_medico"] != session["user_id"]:
        return None
    return consulta


@consultas_bp.post("")
@login_required(["paciente"])
def crear_consulta():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    descripcion = (data.get("descripcion_sintomas") or "").strip()
    id_medico = data.get("id_medico")
    archivo = request.files.get("imagen")

    if not descripcion or not id_medico:
        return jsonify({"ok": False, "mensaje": "Faltan datos obligatorios."}), 400

    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id_medico FROM MEDICO WHERE id_medico=%s",
                (id_medico,),
            )
            if not cur.fetchone():
                return jsonify({"ok": False, "mensaje": "El médico seleccionado no existe."}), 400

            image_name, image_error = upload_chat_image(archivo)
            if image_error:
                return jsonify({"ok": False, "mensaje": image_error}), 400
            cur.execute(
                """INSERT INTO CONSULTA
                   (descripcion_sintomas, fecha_hora, id_medico, id_paciente)
                   VALUES (%s, NOW(), %s, %s)""",
                (descripcion, int(id_medico), session["user_id"]),
            )
            id_consulta = cur.lastrowid
            cur.execute(
                """INSERT INTO MENSAJE
                   (id_consulta, id_usuario, tipo, contenido, imagen, fecha_hora)
                   VALUES (%s, %s, 'paciente', %s, %s, NOW())""",
                (id_consulta, session["user_id"], descripcion, image_name),
            )
            conn.commit()
            return jsonify({"ok": True, "id_consulta": id_consulta}), 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@consultas_bp.get("/mis-consultas")
@login_required(["paciente"])
def mis_consultas():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.id_consulta, c.fecha_hora, c.estado, c.descripcion_sintomas,
                          CONCAT(u.nombre_usuario, ' ', u.apellido_usuario) AS medico_nombre,
                          e.nombre AS especialidad,
                          (SELECT COUNT(*) FROM MENSAJE m WHERE m.id_consulta=c.id_consulta) AS cantidad_mensajes
                   FROM CONSULTA c
                   JOIN USUARIO u ON u.id_usuario=c.id_medico
                   JOIN MEDICO md ON md.id_medico=c.id_medico
                   JOIN ESPECIALIDAD e ON e.id_especialidad=md.id_especialidad
                   WHERE c.id_paciente=%s
                   ORDER BY c.fecha_hora DESC""",
                (session["user_id"],),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@consultas_bp.get("/pendientes")
@login_required(["medico"])
def pendientes():
    """Devuelve todas las conversaciones asignadas al médico.

    Se conserva el endpoint /pendientes por compatibilidad con el frontend,
    pero ahora incluye también consultas Respondidas para que una conversación
    no desaparezca después de que el médico contesta.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.id_consulta, c.fecha_hora, c.estado, c.descripcion_sintomas,
                          CONCAT(u.nombre_usuario, ' ', u.apellido_usuario) AS paciente_nombre,
                          (SELECT COUNT(*) FROM MENSAJE m WHERE m.id_consulta=c.id_consulta) AS cantidad_mensajes,
                          (SELECT m2.contenido FROM MENSAJE m2
                           WHERE m2.id_consulta=c.id_consulta
                           ORDER BY m2.fecha_hora DESC, m2.id_mensaje DESC LIMIT 1) AS ultimo_mensaje,
                          (SELECT m3.fecha_hora FROM MENSAJE m3
                           WHERE m3.id_consulta=c.id_consulta
                           ORDER BY m3.fecha_hora DESC, m3.id_mensaje DESC LIMIT 1) AS ultimo_mensaje_fecha,
                          (SELECT m4.tipo FROM MENSAJE m4
                           WHERE m4.id_consulta=c.id_consulta
                           ORDER BY m4.fecha_hora DESC, m4.id_mensaje DESC LIMIT 1) AS ultimo_mensaje_tipo
                   FROM CONSULTA c
                   JOIN USUARIO u ON u.id_usuario=c.id_paciente
                   WHERE c.id_medico=%s
                   ORDER BY COALESCE(ultimo_mensaje_fecha, c.fecha_hora) DESC""",
                (session["user_id"],),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@consultas_bp.get("/<int:id_consulta>/mensajes")
@login_required(["paciente", "medico"])
def mensajes(id_consulta):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if not user_can_access_consulta(cur, id_consulta):
                return jsonify({"ok": False, "mensaje": "No tiene acceso a esta consulta."}), 403
            cur.execute(
                """SELECT m.id_mensaje, m.tipo, m.contenido, m.imagen, m.fecha_hora,
                          CONCAT(u.nombre_usuario, ' ', u.apellido_usuario) AS nombre_usuario
                   FROM MENSAJE m
                   JOIN USUARIO u ON u.id_usuario=m.id_usuario
                   WHERE m.id_consulta=%s
                   ORDER BY m.fecha_hora ASC, m.id_mensaje ASC""",
                (id_consulta,),
            )
            return jsonify(cur.fetchall())
    finally:
        conn.close()


@consultas_bp.post("/<int:id_consulta>/mensajes")
@login_required(["paciente", "medico"])
def enviar_mensaje(id_consulta):
    contenido = (request.form.get("contenido") or "").strip()
    archivo = request.files.get("imagen")
    if not contenido and not archivo:
        return jsonify({"ok": False, "mensaje": "Escribí un mensaje o adjuntá una imagen."}), 400

    conn = get_connection()
    try:
        conn.begin()
        with conn.cursor() as cur:
            consulta = user_can_access_consulta(cur, id_consulta)
            if not consulta:
                return jsonify({"ok": False, "mensaje": "No tiene acceso a esta consulta."}), 403

            image_name, image_error = upload_chat_image(archivo)
            if image_error:
                return jsonify({"ok": False, "mensaje": image_error}), 400

            tipo = session["rol"]
            cur.execute(
                """INSERT INTO MENSAJE
                   (id_consulta, id_usuario, tipo, contenido, imagen, fecha_hora)
                   VALUES (%s, %s, %s, %s, %s, NOW())""",
                (id_consulta, session["user_id"], tipo, contenido or None, image_name),
            )

            if tipo == "paciente":
                # El mensaje del paciente vuelve a poner el caso en revisión.
                cur.execute(
                    "UPDATE CONSULTA SET estado='En Revision' WHERE id_consulta=%s",
                    (id_consulta,),
                )

            conn.commit()
            return jsonify({"ok": True}), 201
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@consultas_bp.get("/imagen/<path:filename>")
@login_required(["paciente", "medico"])
def imagen(filename):
    # Las imágenes se guardan con nombres aleatorios y esta ruta no se usa como
    # descarga pública desde HTML. Para el proyecto escolar, la autenticación
    # del endpoint evita que la carpeta quede abierta directamente.
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", "chat")
    return send_from_directory(upload_dir, filename)
