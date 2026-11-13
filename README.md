# Plantilla: Flask + CRUD + Postgres (dockerizado)

Base reutilizable para cualquier entrega que pida "una app con CRUD sobre
una base de datos" (p. ej. el TPI de Seminario DevOps). Un solo recurso
(`tareas`) a propósito: demuestra el CRUD completo sin sobreingeniería.
Para un proyecto real, se cambia el modelo de `app.py` por el que corresponda
y el resto de la plantilla (Dockerfile, compose, patrón de rutas) se mantiene.

## Cómo correrlo

```bash
docker compose up -d --build
```

La API queda en `http://localhost:5000`. Postgres queda accesible en el
puerto `5432` (usuario `app`, contraseña `app`, base `app`) por si querés
inspeccionarla con un cliente como DBeaver o `psql`.

Para bajarlo todo (y borrar los datos de la base):

```bash
docker compose down -v
```

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/` | Lista de endpoints disponibles |
| GET | `/tareas` | Lista todas las tareas |
| POST | `/tareas` | Crea una tarea. Body: `{"titulo": "...", "hecha": false}` |
| GET | `/tareas/<id>` | Trae una tarea puntual (404 si no existe) |
| PUT | `/tareas/<id>` | Actualiza `titulo` y/o `hecha` (404 si no existe) |
| DELETE | `/tareas/<id>` | Borra una tarea (404 si no existe, 204 si la borró) |

## Validaciones ya incluidas

- `titulo` vacío o ausente → 400.
- ID inexistente en GET/PUT/DELETE → 404.
- La app espera a que Postgres esté lista antes de crear las tablas
  (reintenta unos segundos en vez de romperse en el primer arranque).

## Estructura

- `app.py` — la API (Flask + SQLAlchemy).
- `Dockerfile` — imagen de la API.
- `docker-compose.yml` — levanta la API y Postgres juntos.
- `requirements.txt` — dependencias.
