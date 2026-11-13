"""
Tests de la API, pensados para correr con `pytest` sin Docker ni Postgres:
usan una base SQLite de prueba, descartable, por cada test.
"""
import pytest

from app import create_app, db


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(f"sqlite:///{db_path}")
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

    with app.test_client() as cliente:
        yield cliente

    with app.app_context():
        db.drop_all()


def test_crear_y_listar_tarea(client):
    respuesta = client.post("/tareas", json={"titulo": "Estudiar sockets"})
    assert respuesta.status_code == 201
    assert respuesta.get_json()["titulo"] == "Estudiar sockets"

    respuesta = client.get("/tareas")
    assert respuesta.status_code == 200
    tareas = respuesta.get_json()
    assert len(tareas) == 1
    assert tareas[0]["hecha"] is False


def test_crear_tarea_sin_titulo_devuelve_400(client):
    respuesta = client.post("/tareas", json={"titulo": "   "})
    assert respuesta.status_code == 400
    assert "error" in respuesta.get_json()


def test_actualizar_y_borrar_tarea(client):
    creada = client.post("/tareas", json={"titulo": "Repasar TLS"}).get_json()
    tarea_id = creada["id"]

    actualizada = client.put(f"/tareas/{tarea_id}", json={"hecha": True})
    assert actualizada.status_code == 200
    assert actualizada.get_json()["hecha"] is True

    borrada = client.delete(f"/tareas/{tarea_id}")
    assert borrada.status_code == 204

    inexistente = client.get(f"/tareas/{tarea_id}")
    assert inexistente.status_code == 404
