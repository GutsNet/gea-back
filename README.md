# GEA - Backend (gea-back)

Plataforma de Control Fitosanitario — Universidad Tecnológica de Tula-Tepeji (UTTT).

API REST desarrollada en **Django + Django REST Framework**, con **MariaDB** como motor de base de datos. Este repositorio construye la imagen de contenedor de la aplicación (`app`), la cual sirve tanto la API como el frontend compilado (SPA de Vue/Vuetify) que proviene del repositorio [`gea-front`](../gea-front).

---

## 1. Descripción del proyecto

G.E.A. (Gestión Ecológica Arbórea) es un sistema para el inventario, monitoreo fitosanitario y gestión de recolección de biomasa de los árboles del campus UTTT. Permite a estudiantes y coordinadores registrar reportes de infestación (escala Hawksworth), dar seguimiento al estado de cada árbol, visualizar un mapa del campus con mapa de calor de infestación, y llevar el control de kilogramos recolectados por brigadas de estudiantes.

## 2. Stack tecnológico

| Componente        | Tecnología                                   |
|-------------------|-----------------------------------------------|
| Lenguaje          | Python 3.12                                   |
| Framework         | Django 5.x + Django REST Framework            |
| Base de datos     | MariaDB 10.x (driver `mysqlclient`)           |
| Autenticación     | JWT (`djangorestframework-simplejwt`)         |
| Servidor WSGI     | Gunicorn                                      |
| Archivos estáticos| WhiteNoise (o Nginx delante, según ambiente)  |
| Contenerización   | Docker / docker-compose                       |
| CI/CD             | GitHub Actions y/o Jenkins                    |

## 3. Roles del sistema

| Rol          | Descripción                                                        |
|--------------|---------------------------------------------------------------------|
| Sysadmin (root)     | Acceso total: usuarios, configuración, todos los módulos            |
| Coordinador (admin)  | Valida/rechaza reportes, gestiona árboles, estudiantes y recolección |
| Brigadista (user)   | Registra reportes de infestación y recolecciones asignadas          |

## 4. Módulos / Apps de Django

| App            | Responsabilidad                                                             |
|----------------|-------------------------------------------------------------------------------|
| `usuarios`     | Login, roles, permisos, perfil                                               |
| `arboles`      | Catálogo de árboles (ID `ARB-XXXX`), especies, historial de reportes por árbol |
| `reportes`     | Alta de reportes de infestación, flujo de validación/rechazo                  |
| `recoleccion`  | Registro de kg recolectados por fecha, ubicación y responsable                |
| `estudiantes`  | Gestión de estudiantes participantes y su actividad                          |
| `dashboard`    | Endpoints agregados: resumen general, evolución de reportes, mapa de calor    |
| `core`         | Utilidades compartidas: paginación, excepciones, manejo de imágenes           |

## 5. Estructura de carpetas

```
gea-back/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py
│   └── settings/
│       ├── base.py
│       ├── dev.py
│       ├── prod.py
│       └── test.py
├── apps/
│   ├── usuarios/
│   ├── arboles/
│   ├── reportes/
│   ├── recoleccion/
│   ├── estudiantes/
│   ├── dashboard/
│   └── core/
├── static/
├── staticfiles/            # generado por collectstatic (gitignored)
├── frontend_dist/          # build de gea-front copiado aquí (gitignored)
├── media/                  # imágenes de árboles/reportes
├── templates/
│   └── index.html
├── docker/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .github/workflows/
│   ├── ci.yml
│   └── build-and-push.yml
├── Jenkinsfile
└── README.md
```

## 6. Modelos principales (resumen)

- **Arbol**: `id_arbol` (ARB-XXXX), especie, nombre científico, ubicación, coordenadas (lat/lng), nivel de infestación actual, estado (Validado/Rechazado/En revisión/Pendiente), fecha de registro, registrado_por.
- **Especie**: nombre común, nombre científico, es_nativa (bool).
- **Reporte**: árbol (FK), nivel de infestación (Hawksworth: 0 / 3.5 / 7.5 / muerto), observaciones, imágenes, estado, reportado_por, fecha.
- **Recoleccion**: fecha, ubicación, kg recolectados, responsable (FK estudiante/usuario).
- **Estudiante**: nombre, matrícula, grupo, kg recolectados (acumulado), estado (Activo/Inactivo/En pausa).
- **Usuario**: extiende `AbstractUser`, matrícula, rol (Sysadmin/Coordinador/Brigadista), estado, último acceso.

## 7. Variables de entorno (`.env`)

```
DEBUG=False
SECRET_KEY=
ALLOWED_HOSTS=

DB_ENGINE=django.db.backends.mysql
DB_NAME=gea
DB_USER=gea_user
DB_PASSWORD=
DB_HOST=db
DB_PORT=3306

JWT_ACCESS_TOKEN_LIFETIME=60          # minutos
JWT_REFRESH_TOKEN_LIFETIME=1440       # minutos

CORS_ALLOWED_ORIGINS=
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
```

## 8. Desarrollo local

```bash
# Clonar y preparar entorno
python -m venv venv && source venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env

# Levantar solo la base de datos
docker-compose up -d db

# Migraciones y datos iniciales
python manage.py migrate
python manage.py createsuperuser

# Correr servidor de desarrollo
python manage.py runserver
```

> Nota: en desarrollo, el front corre de forma independiente (`yarn dev` en `gea-front`) apuntando a `http://localhost:8000/api`. El `frontend_dist/` solo se usa para el build de producción.

## 9. Docker / Producción

El `Dockerfile` de `docker/` realiza:

1. Instala dependencias Python (`requirements/prod.txt`).
2. Copia el código del backend.
3. Copia `frontend_dist/` (build de `gea-front` generado previamente por el pipeline) a la carpeta que Django sirve como estáticos/SPA.
4. Ejecuta `collectstatic`.
5. Expone el servicio vía Gunicorn.

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

`entrypoint.sh` se encarga de: esperar a que la base de datos esté disponible, aplicar migraciones y levantar Gunicorn.

## 10. CI/CD

- **`ci.yml`**: se ejecuta en cada Pull Request. Corre linting (`flake8`/`ruff`), pruebas unitarias (`pytest`) y verifica migraciones pendientes.
- **`build-and-push.yml`** (o `Jenkinsfile` equivalente): en cada push a `main`/tag:
  1. Descarga o hace checkout del build (`dist/`) generado por el pipeline de `gea-front`.
  2. Copia ese `dist/` a `frontend_dist/`.
  3. Construye la imagen Docker.
  4. Publica la imagen en el registry configurado (GHCR/Docker Hub/ECR).
  5. (Opcional) Despliega automáticamente al ambiente correspondiente.

## 11. Convenciones

- Branching: `main` (producción), `develop` (integración), `feature/*`, `hotfix/*`.
- Toda nueva app Django debe incluir `tests/`, `serializers.py` y registrar sus rutas en `config/urls.py`.

## 12. Conventional Commits

Este repo sigue [Conventional Commits](https://www.conventionalcommits.org/). Formato:

```
<tipo>(<scope>): <descripción en minúsculas, modo imperativo>
```

**Tipos permitidos**

| Tipo       | Uso                                                              |
|------------|-------------------------------------------------------------------|
| `feat`     | Nueva funcionalidad (endpoint, modelo, regla de negocio)          |
| `fix`      | Corrección de bug                                                 |
| `refactor` | Cambio de código sin alterar comportamiento                      |
| `test`     | Agregar o corregir pruebas                                        |
| `docs`     | Cambios en documentación (README, docstrings)                     |
| `chore`    | Tareas de mantenimiento (dependencias, configuración, CI)         |
| `perf`     | Mejoras de rendimiento (queries, índices, cache)                  |
| `build`    | Cambios en Docker, requirements, empaquetado                      |
| `ci`       | Cambios en pipelines de GitHub Actions / Jenkins                  |

**Scopes sugeridos** (alineados a las apps del proyecto): `usuarios`, `arboles`, `reportes`, `recoleccion`, `estudiantes`, `dashboard`, `core`, `auth`, `docker`, `db`.

**Ejemplos**

```
feat(arboles): agregar endpoint de historial de reportes por árbol
fix(reportes): corregir cálculo del índice Hawksworth al validar
refactor(recoleccion): extraer lógica de totales a services.py
test(usuarios): cubrir permisos de rol brigadista
docs(dashboard): documentar endpoints de mapa de calor
chore(build): actualizar mysqlclient a 2.2.x
ci(build-and-push): inyectar frontend_dist antes del build de imagen
fix(auth)!: invalidar tokens al desactivar un usuario
```

> Usar `!` después del scope (o `BREAKING CHANGE:` en el pie del commit) cuando el cambio rompa compatibilidad, por ejemplo un cambio de contrato en un serializer que ya consume `gea-front`.