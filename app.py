"""
Plantilla: API Flask + CRUD + Postgres, todo dockerizado.

Pensada para ser la base de un Trabajo Práctico Integrador (DevOps) o de
cualquier entrega que pida "una app con CRUD sobre una base de datos".
Un solo recurso ("tareas") a propósito: alcanza para demostrar el CRUD
completo sin sobreingeniería. Para el TPI real, cambiá el modelo de abajo
por el de tu proyecto (sigue siendo el mismo patrón).

Usa el patrón "application factory" (`create_app`) solo para que los tests
puedan correr contra una base SQLite de prueba sin necesitar Docker ni
Postgres levantados. En producción (Docker) sigue siendo la misma app de
siempre, apuntando a Postgres.
"""
import os
import time

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

db = SQLAlchemy()


class Tarea(db.Model):
    __tablename__ = "tareas"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    hecha = db.Column(db.Boolean, nullable=False, default=False)

    def to_dict(self):
        return {"id": self.id, "titulo": self.titulo, "hecha": self.hecha}


def create_app(database_url=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://app:app@db:5432/app"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.get("/")
    def home():
        return jsonify({"mensaje": "API de tareas funcionando", "endpoints": [
            "GET /tareas", "POST /tareas", "GET /tareas/<id>",
            "PUT /tareas/<id>", "DELETE /tareas/<id>",
        ]})

    @app.get("/tareas")
    def listar_tareas():
        tareas = Tarea.query.order_by(Tarea.id).all()
        return jsonify([t.to_dict() for t in tareas])

    @app.post("/tareas")
    def crear_tarea():
        datos = request.get_json(silent=True) or {}
        titulo = (datos.get("titulo") or "").strip()
        if not titulo:
            return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400
        tarea = Tarea(titulo=titulo, hecha=bool(datos.get("hecha", False)))
        db.session.add(tarea)
        db.session.commit()
        return jsonify(tarea.to_dict()), 201

    @app.get("/tareas/<int:tarea_id>")
    def obtener_tarea(tarea_id):
        tarea = db.session.get(Tarea, tarea_id)
        if tarea is None:
            return jsonify({"error": "No existe esa tarea"}), 404
        return jsonify(tarea.to_dict())

    @app.put("/tareas/<int:tarea_id>")
    def actualizar_tarea(tarea_id):
        tarea = db.session.get(Tarea, tarea_id)
        if tarea is None:
            return jsonify({"error": "No existe esa tarea"}), 404
        datos = request.get_json(silent=True) or {}
        if "titulo" in datos:
            nuevo_titulo = (datos.get("titulo") or "").strip()
            if not nuevo_titulo:
                return jsonify({"error": "El campo 'titulo' no puede quedar vacío"}), 400
            tarea.titulo = nuevo_titulo
        if "hecha" in datos:
            tarea.hecha = bool(datos["hecha"])
        db.session.commit()
        return jsonify(tarea.to_dict())

    @app.delete("/tareas/<int:tarea_id>")
    def eliminar_tarea(tarea_id):
        tarea = db.session.get(Tarea, tarea_id)
        if tarea is None:
            return jsonify({"error": "No existe esa tarea"}), 404
        db.session.delete(tarea)
        db.session.commit()
        return "", 204

    return app


def esperar_a_la_base(app, intentos=15, espera_seg=2):
    """Postgres tarda unos segundos en estar lista; reintentamos en vez de
    fallar directo en el primer request."""
    for i in range(intentos):
        try:
            with app.app_context():
                db.create_all()
            return
        except OperationalError:
            print(f"Esperando a la base de datos... intento {i + 1}/{intentos}")
            time.sleep(espera_seg)
    raise RuntimeError("La base de datos no respondió a tiempo")


app = create_app()

if __name__ == "__main__":
    esperar_a_la_base(app)
    # Local: siempre 5000. En Render (y la mayoría de los PaaS), el
    # puerto lo asigna la plataforma vía la variable de entorno PORT.
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
