from flask import Blueprint, jsonify
from db import get_connection

especialidades_bp = Blueprint("especialidades", __name__)


@especialidades_bp.get("")
def listar_especialidades():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id_especialidad, nombre FROM ESPECIALIDAD ORDER BY nombre")
            return jsonify(cur.fetchall())
    finally:
        conn.close()
