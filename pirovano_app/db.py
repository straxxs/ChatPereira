import pymysql
from pymysql.cursors import DictCursor
from flask import current_app


def get_connection():
    return pymysql.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        cursorclass=DictCursor,
        autocommit=True,
    )
