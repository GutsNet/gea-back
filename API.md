# Documentación de la API — G.E.A. (Gestión Ecológica Arbórea)

## 1. Descripción general

G.E.A. es una API REST desarrollada en Django y Django REST Framework (DRF) para el control fitosanitario del arbolado del campus de la Universidad Tecnológica de Tula-Tepeji (UTTT). Permite gestionar el inventario de árboles y especies, registrar reportes de infestación mediante la escala Hawksworth, tramitar solicitudes de alta o revisión de árboles/especies, llevar el control de recolección de biomasa y consultar indicadores agregados para un dashboard.

### 1.1 Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | Django 5.x + Django REST Framework |
| Base de datos | MariaDB 10.x en producción (`mysqlclient`); SQLite en entorno local |
| Autenticación | JWT (`djangorestframework-simplejwt`) |
| Servidor WSGI | Gunicorn |
| Archivos estáticos | WhiteNoise |
| Filtros | `django-filter` |
| CORS | `django-cors-headers` |
| Contenerización | Docker / docker-compose |

### 1.2 Prefijo base de la API

Todos los endpoints, salvo el panel de administración de Django, están agrupados bajo el prefijo de versión:

```
/api/v1/
```

El enrutamiento raíz del proyecto (`config/urls.py`) distribuye este prefijo hacia los siguientes módulos:

| Prefijo | Módulo (app Django) |
|---|---|
| `/api/v1/auth/` | `apps.usuarios` |
| `/api/v1/arboles/` | `apps.arboles` |
| `/api/v1/reportes/` | `apps.reportes` |
| `/api/v1/recoleccion/` | `apps.recoleccion` |
| `/api/v1/solicitudes/` | `apps.solicitudes` |
| `/api/v1/dashboard/` | `apps.dashboard` |

Adicionalmente existe `/admin/` (panel de administración de Django, fuera del alcance de esta documentación de API) y, en modo `DEBUG`, `/__debug__/` (Django Debug Toolbar) y el servido de archivos `MEDIA_URL`.

### 1.3 Roles del sistema

| Rol | Descripción |
|---|---|
| `Root` | Acceso total al sistema, incluida la gestión de usuarios. |
| `Administrativo` | Valida y revisa solicitudes y reportes; gestiona árboles, especies, ubicaciones y usuarios en modo lectura. |
| `Estudiante` | Crea solicitudes, reportes (a través de solicitudes) y registra recolecciones; ve únicamente sus propios recursos, salvo excepciones señaladas. |

### 1.4 Autenticación

La API utiliza JSON Web Tokens mediante `rest_framework_simplejwt`.

- Esquema de autenticación por defecto: `rest_framework_simplejwt.authentication.JWTAuthentication`.
- Esquema de permisos por defecto: `IsAuthenticated` (todo endpoint requiere autenticación salvo que se indique lo contrario explícitamente).
- Encabezado requerido en cada petición autenticada:

```
Authorization: Bearer <access_token>
```

- El campo de inicio de sesión (`USERNAME_FIELD`) del modelo de usuario es `matricula`, no `username`.
- Configuración de tokens (`SIMPLE_JWT`):

| Parámetro | Valor por defecto | Configurable vía entorno |
|---|---|---|
| `ACCESS_TOKEN_LIFETIME` | 60 minutos | `JWT_ACCESS_TOKEN_LIFETIME` |
| `REFRESH_TOKEN_LIFETIME` | 1440 minutos (24 h) | `JWT_REFRESH_TOKEN_LIFETIME` |
| `ROTATE_REFRESH_TOKENS` | `True` | — |
| `BLACKLIST_AFTER_ROTATION` | `True` | — |
| `AUTH_HEADER_TYPES` | `Bearer` | — |

Al rotar el refresh token (`ROTATE_REFRESH_TOKENS=True`), el refresh token anterior queda invalidado (`BLACKLIST_AFTER_ROTATION=True`).

### 1.5 Paginación

Clase por defecto: `apps.core.pagination.StandardResultsSetPagination` (basada en `PageNumberPagination`).

| Parámetro de query | Descripción | Valor por defecto | Máximo |
|---|---|---|---|
| `page` | Número de página a consultar | 1 | — |
| `page_size` | Cantidad de elementos por página | 20 | 100 |

Formato de respuesta paginada estándar de DRF:

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

### 1.6 Filtros, búsqueda y ordenamiento

Backends activos por defecto en toda la API:

- `django_filters.rest_framework.DjangoFilterBackend` — filtrado exacto por los campos declarados en `filterset_fields` de cada vista.
- `rest_framework.filters.SearchFilter` — búsqueda de texto libre mediante el parámetro `?search=`, sobre los campos declarados en `search_fields`.
- `rest_framework.filters.OrderingFilter` — ordenamiento mediante el parámetro `?ordering=campo` (o `?ordering=-campo` para orden descendente), sobre los campos declarados en `ordering_fields`.

### 1.7 Formato de fechas

| Tipo | Formato |
|---|---|
| `DateTimeField` | `%Y-%m-%dT%H:%M:%S%z` (ISO 8601 con zona horaria) |
| `DateField` | `%Y-%m-%d` |

Zona horaria del proyecto: `America/Mexico_City` (`USE_TZ = True`).

### 1.8 Formato estándar de errores

Todas las respuestas de error de la API pasan por un manejador de excepciones personalizado (`apps.core.exceptions.custom_exception_handler`) que homogeneiza la salida:

```json
{
  "error": true,
  "message": "Descripción legible del error.",
  "details": { }
}
```

- `message`: mensaje humano derivado de `detail`, `non_field_errors` o el primer elemento de una lista de errores.
- `details` (opcional): solo se incluye cuando existen errores de validación por campo, o cuando la respuesta original de DRF es una lista.

### 1.9 CORS

Orígenes permitidos configurables vía variable de entorno `CORS_ALLOWED_ORIGINS` (lista separada por comas). Valor por defecto:

```
http://localhost:5173,http://localhost:8080
```

### 1.10 Identificadores

La mayoría de los modelos usan `UUIDField` como llave primaria (`Usuario`, `Especie`, `Ubicacion`, `Arbol`, `Reporte`, `Solicitud`, `Recoleccion`). Por lo tanto, todos los parámetros de ruta `{id}` de estos recursos son UUID v4 en formato string.

---

## 2. Módulo: Autenticación y Usuarios (`/api/v1/auth/`)

Modelo base: `Usuario` (extiende `AbstractUser` de Django).

### 2.1 Modelo `Usuario`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único, generado automáticamente. |
| `matricula` | string, único, máx. 20 | Matrícula institucional de la UTTT. Es el campo de login (`USERNAME_FIELD`). |
| `username` | string | Campo requerido adicional (`REQUIRED_FIELDS`), heredado de `AbstractUser`. |
| `rol` | choice: `Root`, `Administrativo`, `Estudiante` | Rol del usuario en el sistema. Por defecto `Estudiante`. |
| `grupo` | string, máx. 20 | Grupo escolar del cuatrimestre vigente. Por defecto `"N/A"`. |
| `cuatrimestre` | entero, 1 a 11 | Período lectivo actual del alumno. Por defecto `1`. |
| `estatus` | booleano | `True` = activo, `False` = inactivo. Por defecto `True`. |
| `fecha_registro` | fecha, autogenerada | Se asigna al crear el registro (`auto_now_add`). |
| `ultimo_acceso` | fecha y hora, nullable | Se actualiza automáticamente en cada login exitoso. |

Propiedades calculadas (no expuestas como campos de serializer, uso interno): `es_root`, `es_administrativo`, `es_estudiante`.

### 2.2 `POST /api/v1/auth/login/`

Autentica a un usuario mediante matrícula y contraseña, y devuelve un par de tokens JWT junto con los datos del usuario.

- **Permisos:** público (`AllowAny`).
- **Serializer de entrada:** `LoginSerializer`.

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `matricula` | string | Sí | Matrícula del usuario. |
| `password` | string | Sí | Contraseña en texto plano. |

**Respuesta `200 OK`:**

```json
{
  "access": "string",
  "refresh": "string",
  "user": {
    "id": "uuid",
    "matricula": "string",
    "rol": "Root | Administrativo | Estudiante",
    "grupo": "string",
    "cuatrimestre": 0,
    "estatus": true,
    "fecha_registro": "YYYY-MM-DD",
    "ultimo_acceso": "YYYY-MM-DDTHH:MM:SS±HHMM"
  }
}
```

**Errores posibles:**

- `400 Bad Request` si la matrícula/contraseña son incorrectas (`"Matrícula o contraseña incorrectos."`).
- `400 Bad Request` si la cuenta está desactivada (`"Tu cuenta está desactivada."`).

**Efecto secundario:** al autenticar correctamente, se actualiza el campo `ultimo_acceso` del usuario a la hora actual.

### 2.3 `POST /api/v1/auth/token/refresh/`

Endpoint estándar de `rest_framework_simplejwt` (`TokenRefreshView`) para renovar el `access token` a partir de un `refresh token` vigente.

- **Permisos:** público.

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `refresh` | string | Sí | Refresh token vigente. |

**Respuesta `200 OK`:**

```json
{
  "access": "string",
  "refresh": "string"
}
```

Nota: dado que `ROTATE_REFRESH_TOKENS` está activo, la respuesta incluye un nuevo `refresh` token, y el anterior queda invalidado.

### 2.4 `GET /api/v1/auth/perfil/`

Obtiene el perfil del usuario autenticado.

- **Permisos:** usuario autenticado.
- **Serializer de salida:** `UsuarioSerializer`.

**Respuesta `200 OK`:**

```json
{
  "id": "uuid",
  "matricula": "string",
  "rol": "Root | Administrativo | Estudiante",
  "grupo": "string",
  "cuatrimestre": 0,
  "estatus": true,
  "fecha_registro": "YYYY-MM-DD",
  "ultimo_acceso": "YYYY-MM-DDTHH:MM:SS±HHMM"
}
```

### 2.5 `PATCH /api/v1/auth/perfil/`

Actualiza parcialmente el perfil del usuario autenticado. Solo permite modificar sus propios datos limitados.

- **Permisos:** usuario autenticado.
- **Serializer de entrada/salida:** `PerfilSerializer`.

**Body de la petición (todos los campos opcionales):**

| Campo | Tipo | Descripción |
|---|---|---|
| `grupo` | string | Nuevo grupo escolar. |
| `cuatrimestre` | entero (1–11) | Nuevo cuatrimestre. |

**Respuesta `200 OK`:**

```json
{
  "grupo": "string",
  "cuatrimestre": 0
}
```

Nota: el método `PUT` está también disponible por herencia de `RetrieveUpdateAPIView`, pero el body de entrada equivale al de `PATCH` ya que el serializer solo expone `grupo` y `cuatrimestre`.

### 2.6 `GET /api/v1/auth/usuarios/`

Lista los usuarios del sistema.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo` (solo Root y Administrativo).
- **Serializer de salida:** `UsuarioSerializer`.
- **Paginación:** estándar (20 por página, máx. 100).
- **Filtros exactos (`filterset_fields`):** `rol`, `estatus`, `grupo`, `cuatrimestre`.
- **Búsqueda (`search_fields`):** `matricula`, `username`.
- **Ordenamiento (`ordering_fields`):** `fecha_registro`, `matricula`, `ultimo_acceso`.

**Ejemplo de uso:** `GET /api/v1/auth/usuarios/?rol=Estudiante`

**Respuesta `200 OK`:** lista paginada de objetos `Usuario` (ver formato en 2.4).

### 2.7 `POST /api/v1/auth/usuarios/`

Crea un nuevo usuario.

- **Permisos:** `IsAuthenticated` + `IsRoot` (solo Root).
- **Serializer de entrada:** `UsuarioCreateSerializer`.

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `matricula` | string | Sí | Matrícula institucional, única. |
| `username` | string | Sí | Nombre de usuario. |
| `password` | string, mín. 8 caracteres | Sí | Contraseña (se almacena hasheada). |
| `rol` | choice: `Root`, `Administrativo`, `Estudiante` | No | Por defecto `Estudiante`. |
| `grupo` | string | No | Por defecto `"N/A"`. |
| `cuatrimestre` | entero (1–11) | No | Por defecto `1`. |
| `estatus` | booleano | No | Por defecto `True`. |

**Respuesta `201 Created`:** objeto de entrada sin la contraseña (equivalente a los campos declarados en `UsuarioCreateSerializer`, excluyendo `password` en la salida por ser `write_only`).

### 2.8 `GET /api/v1/auth/usuarios/{id}/`

Obtiene el detalle de un usuario.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Serializer de salida:** `UsuarioSerializer`.

### 2.9 `PUT /api/v1/auth/usuarios/{id}/` y `PATCH /api/v1/auth/usuarios/{id}/`

Actualiza (total o parcialmente) un usuario existente.

- **Permisos:** `IsAuthenticated` + `IsRoot`.
- **Serializer de entrada/salida:** `UsuarioCreateSerializer` (mismos campos que en la creación; `password` es opcional en `PATCH` pero, si se envía, debe cumplir el mínimo de 8 caracteres).

### 2.10 `DELETE /api/v1/auth/usuarios/{id}/`

Elimina un usuario.

- **Permisos:** `IsAuthenticated` + `IsRoot`.
- **Respuesta:** `204 No Content`.

---

## 3. Módulo: Árboles (`/api/v1/arboles/`)

Este módulo agrupa tres recursos: especies, ubicaciones y árboles. El router registra `especies` y `ubicaciones` como sub-rutas explícitas, y el recurso de árboles se registra en la raíz del módulo (por lo que las rutas de árbol no llevan segmento adicional).

### 3.1 Modelo `Especie`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `nombre` | string, máx. 100 | Nombre común de la especie. |
| `nombre_cientifico` | string, único, máx. 150 | Nomenclatura binominal científica. |
| `nativa` | booleano | `True` si la especie es originaria de la región. Por defecto `False`. |

### 3.2 Modelo `Ubicacion`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `nombre` | string, único, máx. 100 | Nombre amigable de la ubicación. |
| `coordenadas` | string, único, máx. 500 | Estructura de datos compuesta con la información geoespacial (celda Voronoi) del área. |

### 3.3 Modelo `Arbol`

Incluye `TimestampMixin` (`created_at`, `updated_at`, autogenerados).

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `especie` | FK → `Especie` (`PROTECT`) | Especie del árbol. |
| `id_area` | FK → `Ubicacion` (`PROTECT`) | Ubicación/celda a la que pertenece. |
| `coordenadas` | string, máx. 500, opcional | Punto exacto del árbol (`lat,long` o `x,y`). |
| `etiqueta` | string, máx. 50 | Código alfanumérico identificador del árbol. |
| `nivel_infestacion` | float | Suma de los 3 niveles Hawksworth del último censo. Rango: 0.0 a 7.5. Por defecto `0.0`. |
| `estado` | choice: `Sano`, `Infestado`, `Limpieza`, `Saneado` | Estado fitosanitario. Por defecto `Sano`. |
| `fecha_reporte` | fecha | Fecha del último cambio de estatus fitosanitario. |
| `imagen1`…`imagen4` | string, máx. 500, opcional | Rutas relativas de hasta 4 imágenes de evidencia. |
| `created_at` / `updated_at` | fecha y hora | Timestamps automáticos. |

### 3.4 `GET /api/v1/arboles/especies/`

Lista las especies registradas.

- **Permisos:** cualquier usuario autenticado.
- **Serializer:** `EspecieSerializer`.
- **Búsqueda:** `nombre`, `nombre_cientifico`.
- **Filtros exactos:** `nativa`.

**Objeto `Especie` (formato de respuesta):**

```json
{
  "id": "uuid",
  "nombre": "string",
  "nombre_cientifico": "string",
  "nativa": true
}
```

### 3.5 `POST /api/v1/arboles/especies/`

Crea una especie.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Body:** `nombre` (string, requerido), `nombre_cientifico` (string, único, requerido), `nativa` (booleano, opcional).

### 3.6 `GET /api/v1/arboles/especies/{id}/`

Detalle de una especie. Mismos permisos y formato que 3.4.

### 3.7 `PUT` / `PATCH /api/v1/arboles/especies/{id}/`

Actualiza una especie (total o parcial).

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Body:** mismos campos que la creación.

### 3.8 `DELETE /api/v1/arboles/especies/{id}/`

Elimina una especie.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Nota:** la relación con `Arbol.especie` usa `on_delete=PROTECT`; si existen árboles asociados, la base de datos rechazará el borrado.
- **Respuesta:** `204 No Content` (o error de integridad referencial si hay árboles dependientes).

### 3.9 `GET /api/v1/arboles/ubicaciones/`

Lista las ubicaciones (celdas Voronoi).

- **Permisos:** cualquier usuario autenticado.
- **Serializer:** `UbicacionSerializer`.
- **Búsqueda:** `nombre`, `coordenadas`.

**Objeto `Ubicacion` (formato de respuesta):**

```json
{
  "id": "uuid",
  "nombre": "string",
  "coordenadas": "string"
}
```

### 3.10 `POST /api/v1/arboles/ubicaciones/`

Crea una ubicación.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Body:** `nombre` (string, único, requerido), `coordenadas` (string, único, requerido).

### 3.11 `GET /api/v1/arboles/ubicaciones/{id}/`

Detalle de una ubicación. Mismos permisos y formato que 3.9.

### 3.12 `PUT` / `PATCH /api/v1/arboles/ubicaciones/{id}/`

Actualiza una ubicación.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.

### 3.13 `DELETE /api/v1/arboles/ubicaciones/{id}/`

Elimina una ubicación.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Nota:** la relación con `Arbol.id_area` usa `on_delete=PROTECT`; si existen árboles asociados, el borrado será rechazado a nivel de base de datos.

### 3.14 `GET /api/v1/arboles/`

Lista los árboles del catálogo.

- **Permisos:** cualquier usuario autenticado.
- **Serializer:** `ArbolListSerializer` (versión compacta, exclusiva para listado).
- **Filtros exactos:** `especie`, `estado`, `id_area`.
- **Búsqueda:** `etiqueta`, `especie__nombre`.
- **Ordenamiento:** `fecha_reporte`, `nivel_infestacion`, `etiqueta`.

**Objeto `Arbol` en listado:**

```json
{
  "id": "uuid",
  "etiqueta": "string",
  "especie": "uuid",
  "especie_nombre": "string",
  "id_area": "uuid",
  "coordenadas": "string",
  "nivel_infestacion": 0.0,
  "estado": "Sano | Infestado | Limpieza | Saneado",
  "fecha_reporte": "YYYY-MM-DD"
}
```

### 3.15 `POST /api/v1/arboles/`

Crea un árbol.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Serializer:** `ArbolSerializer` (versión completa).

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `especie` | uuid (FK) | Sí | ID de la especie. |
| `id_area` | uuid (FK) | Sí | ID de la ubicación. |
| `coordenadas` | string | No | Punto exacto del árbol. |
| `etiqueta` | string | Sí | Código alfanumérico. |
| `nivel_infestacion` | float | No | Por defecto `0.0`. |
| `estado` | choice | No | Por defecto `Sano`. |
| `fecha_reporte` | fecha (`YYYY-MM-DD`) | Sí | Fecha de último reporte. |
| `imagen1`…`imagen4` | string | No | Rutas de imágenes de evidencia. |

**Respuesta `201 Created`:** objeto completo (ver 3.16).

### 3.16 `GET /api/v1/arboles/{id}/`

Detalle de un árbol.

- **Permisos:** cualquier usuario autenticado.
- **Serializer:** `ArbolSerializer` (versión completa, con detalle anidado de especie y ubicación).

**Formato de respuesta:**

```json
{
  "id": "uuid",
  "etiqueta": "string",
  "especie": "uuid",
  "especie_detail": {
    "id": "uuid",
    "nombre": "string",
    "nombre_cientifico": "string",
    "nativa": true
  },
  "id_area": "uuid",
  "ubicacion_detail": {
    "id": "uuid",
    "nombre": "string",
    "coordenadas": "string"
  },
  "coordenadas": "string",
  "nivel_infestacion": 0.0,
  "estado": "Sano | Infestado | Limpieza | Saneado",
  "fecha_reporte": "YYYY-MM-DD",
  "imagen1": "string",
  "imagen2": "string",
  "imagen3": "string",
  "imagen4": "string",
  "created_at": "YYYY-MM-DDTHH:MM:SS±HHMM",
  "updated_at": "YYYY-MM-DDTHH:MM:SS±HHMM"
}
```

### 3.17 `PUT` / `PATCH /api/v1/arboles/{id}/`

Actualiza un árbol (total o parcial).

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Body:** mismos campos que la creación (3.15).

### 3.18 `DELETE /api/v1/arboles/{id}/`

Elimina un árbol.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo`.
- **Respuesta:** `204 No Content`.
- **Nota:** los reportes asociados (`Reporte.id_arbol`) se eliminan en cascada (`on_delete=CASCADE`).

---

## 4. Módulo: Reportes (`/api/v1/reportes/`)

Módulo de solo lectura. Los reportes se generan automáticamente al aceptar una solicitud (ver sección 6); no existe endpoint de creación directa ni de edición manual.

### 4.1 Modelo `Reporte`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `id_arbol` | FK → `Arbol` (`CASCADE`) | Árbol reportado. |
| `responsable` | FK → `Usuario` (`SET_NULL`, nullable) | Usuario que generó el reporte. |
| `n1` | float, 0.0–2.5 | Medición Hawksworth — componente 1. |
| `n2` | float, 0.0–2.5 | Medición Hawksworth — componente 2. |
| `n3` | float, 0.0–2.5 | Medición Hawksworth — componente 3. |
| `status_reporte` | choice: `Validado`, `Rechazado` | Estatus del reporte. |
| `hora` | fecha y hora | Timestamp exacto de transmisión del reporte. |
| `observaciones` | texto, opcional | Notas complementarias. |

Propiedad calculada: `nivel_infestacion_promedio` = `n1 + n2 + n3` (redondeado a 2 decimales, máximo 7.5).

### 4.2 `GET /api/v1/reportes/`

Lista los reportes.

- **Permisos:** `IsAuthenticated`.
- **Serializer:** `ReporteListSerializer`.
- **Filtros exactos:** `id_arbol`, `status_reporte`, `responsable`.
- **Búsqueda:** `id_arbol__etiqueta`, `observaciones`.
- **Ordenamiento:** `hora`.

**Reglas de visibilidad:**

- Si se envía el parámetro de query `id_arbol`, cualquier usuario autenticado puede ver todos los reportes de ese árbol (uso previsto para el mapa del campus).
- Si no se envía `id_arbol`, los usuarios con `rol = Estudiante` solo ven los reportes donde ellos son `responsable`. Administrativos y Root ven todos.

**Ejemplo de uso:** `GET /api/v1/reportes/?id_arbol={uuid}`

**Objeto `Reporte` en listado:**

```json
{
  "id": "uuid",
  "id_arbol": "uuid",
  "arbol_etiqueta": "string",
  "n1": 0.0,
  "n2": 0.0,
  "n3": 0.0,
  "nivel_infestacion": 0.0,
  "status_reporte": "Validado | Rechazado",
  "hora": "YYYY-MM-DDTHH:MM:SS±HHMM",
  "responsable_matricula": "string"
}
```

### 4.3 `GET /api/v1/reportes/{id}/`

Detalle de un reporte.

- **Permisos:** `IsAuthenticated` (sujeto a las mismas reglas de visibilidad de 4.2 vía `get_queryset`).
- **Serializer:** `ReporteSerializer`.

**Formato de respuesta:**

```json
{
  "id": "uuid",
  "id_arbol": "uuid",
  "arbol_etiqueta": "string",
  "responsable": "uuid",
  "responsable_matricula": "string",
  "n1": 0.0,
  "n2": 0.0,
  "n3": 0.0,
  "nivel_infestacion": 0.0,
  "status_reporte": "Validado | Rechazado",
  "hora": "YYYY-MM-DDTHH:MM:SS±HHMM",
  "observaciones": "string"
}
```

Nota técnica: aunque el `ViewSet` solo expone `list` y `retrieve` (`mixins.ListModelMixin`, `mixins.RetrieveModelMixin`), el archivo de serializers define también `ReporteSerializer.create()` y `ValidarReporteSerializer`, pensados para una eventual creación/validación manual de reportes; actualmente no están conectados a ninguna ruta activa.

---

## 5. Módulo: Recolección (`/api/v1/recoleccion/`)

Registro de kilogramos de biomasa (heno motita) recolectados por estudiantes. El registro en el sistema no lo hace el propio estudiante, sino un Administrativo/Root, ya que es quien recibe, pesa y captura la recolección a nombre del estudiante que la realizó físicamente.

### 5.1 Modelo `Recoleccion`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `responsable` | FK → `Usuario` (`SET_NULL`, nullable) | Estudiante que realizó la recolección. |
| `kilos` | float | Masa en kg registrada en la báscula institucional. |
| `fecha` | fecha | Fecha del registro físico y validación del pesaje. |

### 5.2 `GET /api/v1/recoleccion/`

Lista los registros de recolección.

- **Permisos:** `IsAuthenticated`.
- **Serializer:** `RecoleccionSerializer`.
- **Filtros exactos:** `responsable`, `fecha`.
- **Ordenamiento:** `fecha`, `kilos`.
- **Visibilidad:** los usuarios con `rol = Estudiante` solo ven sus propios registros (`responsable = request.user`). Administrativos y Root ven todos.

**Objeto `Recoleccion` (formato de respuesta):**

```json
{
  "id": "uuid",
  "responsable": "uuid",
  "responsable_matricula": "string",
  "kilos": 0.0,
  "fecha": "YYYY-MM-DD"
}
```

### 5.3 `POST /api/v1/recoleccion/`

Registra una nueva recolección.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo` (solo Administrativo y Root; un Estudiante recibe `403 Forbidden`).
- **Body:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `responsable` | uuid (FK) | Sí | ID del estudiante que realizó la recolección. Debe corresponder a un usuario con `rol = "Estudiante"`; de lo contrario, error de validación: `"El responsable de una recolección debe ser un estudiante."`. |
| `kilos` | float | Sí | Masa registrada en la báscula. |
| `fecha` | fecha (`YYYY-MM-DD`) | Sí | Fecha del pesaje. |

- **Efecto:** a diferencia de otros módulos (`reportes`, `solicitudes`), aquí `responsable` **no** se asigna automáticamente al usuario autenticado; lo indica explícitamente quien captura el registro (el Administrativo/Root), ya que el estudiante no es quien realiza la petición.
- **Respuesta:** `201 Created` con el objeto creado.

### 5.4 `GET /api/v1/recoleccion/{id}/`

Detalle de una recolección. Mismos permisos y visibilidad que 5.2.

### 5.5 `PUT` / `PATCH /api/v1/recoleccion/{id}/`

Actualiza una recolección.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo` (solo Administrativo y Root).
- **Body:** `responsable`, `kilos`, `fecha` (según sea `PUT` o `PATCH`).

### 5.6 `DELETE /api/v1/recoleccion/{id}/`

Elimina una recolección.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo` (solo Administrativo y Root).
- **Respuesta:** `204 No Content`.

---

## 6. Módulo: Solicitudes (`/api/v1/solicitudes/`)

Flujo mediante el cual un estudiante propone el alta de un árbol y/o especie nuevos (o reporta uno existente), y un Administrativo/Root la revisa. Al aceptar la solicitud, el sistema crea automáticamente las entidades correspondientes (`Especie`, `Arbol`, `Reporte`) dentro de una transacción atómica.

### 6.1 Modelo `Solicitud`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único. |
| `solicitante` | FK → `Usuario` (`CASCADE`) | Usuario que envía la solicitud. |
| `status` | choice: `Pendiente`, `Aceptada`, `Rechazada` | Estatus de la solicitud. Por defecto `Pendiente`. |
| `fecha_solicitud` | fecha y hora, autogenerada | Fecha de envío (`auto_now_add`). |
| `especie_existente` | FK → `Especie` (`SET_NULL`, opcional) | Especie ya registrada, si aplica. |
| `nueva_especie_nombre` | string, opcional | Nombre común de una especie nueva propuesta. |
| `nueva_especie_nombre_cientifico` | string, opcional | Nombre científico de la especie nueva. |
| `nueva_especie_nativa` | booleano, nullable | Si la especie nueva es nativa. |
| `arbol_existente` | FK → `Arbol` (`SET_NULL`, opcional) | Árbol ya registrado, si aplica. |
| `nueva_etiqueta` | string, opcional | Etiqueta de un árbol nuevo propuesto. |
| `id_area` | FK → `Ubicacion` (`SET_NULL`, opcional) | Ubicación del árbol nuevo. |
| `coordenadas_exactas` | string, opcional | Coordenadas exactas del árbol nuevo. |
| `n1`, `n2`, `n3` | float, 0.0–2.5 c/u | Mediciones Hawksworth. |
| `observaciones` | texto, opcional | Notas de evidencia. |
| `imagen1`…`imagen4` | string, opcional | Rutas de imágenes de evidencia. |
| `revisado_por` | FK → `Usuario` (`SET_NULL`, opcional) | Administrativo/Root que revisó la solicitud. |
| `fecha_revision` | fecha y hora, opcional | Fecha en que se resolvió la solicitud. |
| `motivo_rechazo` | texto, opcional | Motivo indicado en caso de rechazo. |

Propiedades calculadas: `es_especie_nueva`, `es_arbol_nuevo`, `nivel_infestacion_promedio` (suma de `n1+n2+n3`, redondeada a 2 decimales).

### 6.2 `GET /api/v1/solicitudes/`

Lista las solicitudes.

- **Permisos:** `IsAuthenticated`.
- **Serializer:** `SolicitudListSerializer`.
- **Filtros exactos:** `status`, `solicitante`.
- **Búsqueda:** `nueva_etiqueta`, `arbol_existente__etiqueta`, `observaciones`.
- **Ordenamiento:** `fecha_solicitud`, `status`.
- **Visibilidad:** los usuarios con `rol = Estudiante` solo ven sus propias solicitudes (`solicitante = request.user`). Administrativos y Root ven todas.

**Objeto `Solicitud` en listado:**

```json
{
  "id": "uuid",
  "solicitante_matricula": "string",
  "status": "Pendiente | Aceptada | Rechazada",
  "fecha_solicitud": "YYYY-MM-DDTHH:MM:SS±HHMM",
  "arbol_existente": "uuid | null",
  "nueva_etiqueta": "string",
  "es_especie_nueva": true,
  "es_arbol_nuevo": true,
  "n1": 0.0,
  "n2": 0.0,
  "n3": 0.0,
  "nivel_infestacion": 0.0
}
```

### 6.3 `POST /api/v1/solicitudes/`

Crea una nueva solicitud.

- **Permisos:** `IsAuthenticated` (cualquier rol; en la práctica, uso previsto para Estudiantes).
- **Serializer:** `SolicitudCreateSerializer`.
- **Efecto:** el campo `solicitante` se asigna automáticamente al usuario autenticado.

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `especie_existente` | uuid (FK) | Condicional | ID de especie ya registrada. |
| `nueva_especie_nombre` | string | Condicional | Nombre común de especie nueva. |
| `nueva_especie_nombre_cientifico` | string | Condicional | Nombre científico de especie nueva. |
| `nueva_especie_nativa` | booleano | No | Si la especie nueva es nativa. |
| `arbol_existente` | uuid (FK) | Condicional | ID de árbol ya registrado. |
| `nueva_etiqueta` | string | Condicional | Etiqueta de árbol nuevo. |
| `id_area` | uuid (FK) | Condicional | Ubicación del árbol nuevo. |
| `coordenadas_exactas` | string | Condicional | Coordenadas exactas del árbol nuevo. |
| `n1` | float, 0.0–2.5 | Sí | Medición Hawksworth 1. |
| `n2` | float, 0.0–2.5 | Sí | Medición Hawksworth 2. |
| `n3` | float, 0.0–2.5 | Sí | Medición Hawksworth 3. |
| `observaciones` | string | No | Notas adicionales. |
| `imagen1`…`imagen4` | string | No | Rutas de imágenes de evidencia. |

**Reglas de validación (`validate()` del serializer):**

1. Debe existir `arbol_existente`, **o** cumplirse todas las condiciones de árbol nuevo:
   - `nueva_etiqueta` presente.
   - `id_area` presente (de lo contrario: `"Se requiere una ubicación para un árbol nuevo."`).
   - `coordenadas_exactas` no vacío (de lo contrario: `"Se requieren coordenadas exactas para un árbol nuevo."`).
   - `especie_existente` **o** `nueva_especie_nombre` presente (de lo contrario: `"Se requiere una especie (existente o nueva) para un árbol nuevo."`).
2. Si no se envía ni `arbol_existente` ni `nueva_etiqueta`: error `"Debes seleccionar un árbol existente o ingresar los datos de uno nuevo."`.
3. Si se propone una especie nueva (`nueva_especie_nombre`), es obligatorio `nueva_especie_nombre_cientifico` (de lo contrario: `"El nombre científico es requerido para una especie nueva."`).
4. Si se proporciona `arbol_existente`, se omite toda validación de especie (se asume que el árbol ya tiene su especie asignada).

**Respuesta `201 Created`:** objeto creado con los campos de entrada, más `id` generado.

### 6.4 `GET /api/v1/solicitudes/{id}/`

Detalle de una solicitud.

- **Permisos:** `IsAuthenticated` (sujeto a las reglas de visibilidad de 6.2).
- **Serializer:** `SolicitudDetailSerializer`.

**Formato de respuesta:**

```json
{
  "id": "uuid",
  "solicitante": "uuid",
  "solicitante_matricula": "string",
  "status": "Pendiente | Aceptada | Rechazada",
  "fecha_solicitud": "YYYY-MM-DDTHH:MM:SS±HHMM",
  "especie_existente": "uuid | null",
  "nueva_especie_nombre": "string",
  "nueva_especie_nombre_cientifico": "string",
  "nueva_especie_nativa": true,
  "es_especie_nueva": true,
  "arbol_existente": "uuid | null",
  "nueva_etiqueta": "string",
  "id_area": "uuid | null",
  "coordenadas_exactas": "string",
  "es_arbol_nuevo": true,
  "n1": 0.0,
  "n2": 0.0,
  "n3": 0.0,
  "nivel_infestacion": 0.0,
  "observaciones": "string",
  "imagen1": "string",
  "imagen2": "string",
  "imagen3": "string",
  "imagen4": "string",
  "revisado_por": "uuid | null",
  "revisado_por_matricula": "string | null",
  "fecha_revision": "YYYY-MM-DDTHH:MM:SS±HHMM | null",
  "motivo_rechazo": "string"
}
```

### 6.5 `PUT` / `PATCH /api/v1/solicitudes/{id}/`

Actualiza una solicitud existente.

- **Permisos:** `IsAuthenticated`.
- **Serializer:** `SolicitudDetailSerializer` (nótese que los campos de control de flujo — `status`, `solicitante`, `revisado_por`, `fecha_revision`, `motivo_rechazo` — son de solo lectura y no pueden modificarse por esta vía).

### 6.6 `DELETE /api/v1/solicitudes/{id}/`

Elimina una solicitud.

- **Permisos:** `IsAuthenticated`.
- **Respuesta:** `204 No Content`.

### 6.7 `POST /api/v1/solicitudes/{id}/revisar/`

Acción personalizada para aceptar o rechazar una solicitud pendiente.

- **Permisos:** `IsAuthenticated` + `IsAdministrativo` (solo Administrativo y Root).
- **Serializer de entrada:** `RevisarSolicitudSerializer`.

**Body de la petición:**

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `accion` | choice: `Aceptada`, `Rechazada` | Sí | Decisión sobre la solicitud. |
| `motivo_rechazo` | string | No (recomendado si `accion = Rechazada`) | Justificación del rechazo. Por defecto cadena vacía. |

**Precondición:** la solicitud debe estar en estatus `Pendiente`; si ya fue revisada, responde `400 Bad Request`:

```json
{
  "error": true,
  "message": "Esta solicitud ya fue revisada."
}
```

**Comportamiento al aceptar (`accion = "Aceptada"`):** ejecuta `aceptar_solicitud()` en una transacción atómica:

1. Si la solicitud propone una especie nueva (`es_especie_nueva`), crea un registro `Especie` con `nombre`, `nombre_cientifico` y `nativa` tomados de la solicitud.
2. Si la solicitud propone un árbol nuevo (`es_arbol_nuevo`), crea un registro `Arbol` con la especie resuelta en el paso anterior (o la existente), la ubicación (`id_area`), coordenadas exactas, etiqueta, nivel de infestación calculado, estado calculado, fecha de reporte (fecha actual) e imágenes de evidencia.
3. Crea un `Reporte` con estatus `Validado`, asociado al árbol resuelto, con `responsable` igual al solicitante original, las mediciones `n1`, `n2`, `n3`, la hora igual a `fecha_solicitud` y las observaciones de la solicitud.
4. Actualiza el árbol (nuevo o existente) con el nuevo `nivel_infestacion`, el `estado` recalculado y la `fecha_reporte` igual a la fecha actual.
5. Marca la solicitud como `Aceptada`, registrando `revisado_por` (el administrador que aprobó) y `fecha_revision` (momento actual).

**Regla de cálculo de estado fitosanitario (`_calcular_estado`):**

- `nivel_infestacion == 0` → `Sano`.
- `nivel_infestacion > 0` → `Infestado`.

**Comportamiento al rechazar (`accion = "Rechazada"`):** ejecuta `rechazar_solicitud()`:

1. Marca la solicitud como `Rechazada`.
2. Registra `revisado_por`, `fecha_revision` y `motivo_rechazo` (tomado del body, o cadena vacía si no se envía).
3. No se crea ninguna entidad adicional.

**Respuesta `200 OK`:** objeto `Solicitud` actualizado, en el formato de `SolicitudDetailSerializer` (ver 6.4).

---

## 7. Módulo: Dashboard (`/api/v1/dashboard/`)

Endpoints de solo lectura que agregan datos para alimentar visualizaciones (gráficas tipo ApexCharts y mapa de calor tipo Leaflet en el frontend). No exponen modelos propios; consultan directamente `Arbol`, `Especie`, `Reporte`, `Recoleccion` y `Usuario`.

### 7.1 `GET /api/v1/dashboard/resumen/`

Indicadores generales (KPIs) del sistema.

- **Permisos:** `IsAuthenticated`.
- **Parámetros:** ninguno.

**Respuesta `200 OK`:**

```json
{
  "arboles": {
    "total": 0,
    "sanos": 0,
    "infestados": 0,
    "en_limpieza": 0,
    "saneados": 0
  },
  "reportes": {
    "total": 0,
    "validados": 0,
    "rechazados": 0
  },
  "kg_recolectados": 0.0,
  "estudiantes_activos": 0
}
```

`estudiantes_activos` cuenta los usuarios con `rol = "Estudiante"` y `estatus = True`.

### 7.2 `GET /api/v1/dashboard/evolucion-reportes/`

Serie temporal de reportes agrupados por mes, ordenada cronológicamente.

- **Permisos:** `IsAuthenticated`.
- **Parámetros:** ninguno.

**Respuesta `200 OK`:**

```json
[
  {
    "mes": "YYYY-MM-DDTHH:MM:SS±HHMM",
    "total": 0,
    "validados": 0,
    "rechazados": 0
  }
]
```

El campo `mes` corresponde al truncamiento a nivel mes (`TruncMonth`) del campo `hora` de cada reporte.

### 7.3 `GET /api/v1/dashboard/mapa-calor/`

Listado de árboles con su ubicación y nivel de infestación, para alimentar un mapa de calor.

- **Permisos:** `IsAuthenticated`.
- **Parámetros:** ninguno.

**Respuesta `200 OK`:**

```json
[
  {
    "etiqueta": "string",
    "nivel_infestacion": 0.0,
    "estado": "Sano | Infestado | Limpieza | Saneado",
    "especie__nombre": "string",
    "id_area__coordenadas": "string"
  }
]
```

### 7.4 `GET /api/v1/dashboard/especies-afectadas/`

Ranking de especies según su número de árboles infestados.

- **Permisos:** `IsAuthenticated`.
- **Parámetros:** ninguno.

**Respuesta `200 OK`:**

```json
[
  {
    "nombre": "string",
    "nombre_cientifico": "string",
    "total_arboles": 0,
    "arboles_infestados": 0,
    "nivel_promedio": 0.0
  }
]
```

**Reglas de la consulta:**

- Solo incluye especies con `total_arboles > 0` (al menos un árbol asociado).
- Ordenado de forma descendente por `arboles_infestados`.
- `nivel_promedio` es el promedio (`Avg`) del `nivel_infestacion` de los árboles de esa especie.

---

## 8. Resumen de rutas

| Método | Ruta | Recurso | Permiso mínimo |
|---|---|---|---|
| POST | `/api/v1/auth/login/` | Login | Público |
| POST | `/api/v1/auth/token/refresh/` | Refrescar token | Público |
| GET | `/api/v1/auth/perfil/` | Perfil propio | Autenticado |
| PATCH | `/api/v1/auth/perfil/` | Perfil propio | Autenticado |
| GET | `/api/v1/auth/usuarios/` | Usuarios (lista) | Administrativo |
| POST | `/api/v1/auth/usuarios/` | Usuarios (crear) | Root |
| GET | `/api/v1/auth/usuarios/{id}/` | Usuarios (detalle) | Administrativo |
| PUT/PATCH | `/api/v1/auth/usuarios/{id}/` | Usuarios (editar) | Root |
| DELETE | `/api/v1/auth/usuarios/{id}/` | Usuarios (eliminar) | Root |
| GET | `/api/v1/arboles/especies/` | Especies (lista) | Autenticado |
| POST | `/api/v1/arboles/especies/` | Especies (crear) | Administrativo |
| GET | `/api/v1/arboles/especies/{id}/` | Especies (detalle) | Autenticado |
| PUT/PATCH | `/api/v1/arboles/especies/{id}/` | Especies (editar) | Administrativo |
| DELETE | `/api/v1/arboles/especies/{id}/` | Especies (eliminar) | Administrativo |
| GET | `/api/v1/arboles/ubicaciones/` | Ubicaciones (lista) | Autenticado |
| POST | `/api/v1/arboles/ubicaciones/` | Ubicaciones (crear) | Administrativo |
| GET | `/api/v1/arboles/ubicaciones/{id}/` | Ubicaciones (detalle) | Autenticado |
| PUT/PATCH | `/api/v1/arboles/ubicaciones/{id}/` | Ubicaciones (editar) | Administrativo |
| DELETE | `/api/v1/arboles/ubicaciones/{id}/` | Ubicaciones (eliminar) | Administrativo |
| GET | `/api/v1/arboles/` | Árboles (lista) | Autenticado |
| POST | `/api/v1/arboles/` | Árboles (crear) | Administrativo |
| GET | `/api/v1/arboles/{id}/` | Árboles (detalle) | Autenticado |
| PUT/PATCH | `/api/v1/arboles/{id}/` | Árboles (editar) | Administrativo |
| DELETE | `/api/v1/arboles/{id}/` | Árboles (eliminar) | Administrativo |
| GET | `/api/v1/reportes/` | Reportes (lista) | Autenticado |
| GET | `/api/v1/reportes/{id}/` | Reportes (detalle) | Autenticado |
| GET | `/api/v1/recoleccion/` | Recolección (lista) | Autenticado |
| POST | `/api/v1/recoleccion/` | Recolección (crear) | Administrativo |
| GET | `/api/v1/recoleccion/{id}/` | Recolección (detalle) | Autenticado |
| PUT/PATCH | `/api/v1/recoleccion/{id}/` | Recolección (editar) | Administrativo |
| DELETE | `/api/v1/recoleccion/{id}/` | Recolección (eliminar) | Administrativo |
| GET | `/api/v1/solicitudes/` | Solicitudes (lista) | Autenticado |
| POST | `/api/v1/solicitudes/` | Solicitudes (crear) | Autenticado |
| GET | `/api/v1/solicitudes/{id}/` | Solicitudes (detalle) | Autenticado |
| PUT/PATCH | `/api/v1/solicitudes/{id}/` | Solicitudes (editar) | Autenticado |
| DELETE | `/api/v1/solicitudes/{id}/` | Solicitudes (eliminar) | Autenticado |
| POST | `/api/v1/solicitudes/{id}/revisar/` | Solicitudes (aceptar/rechazar) | Administrativo |
| GET | `/api/v1/dashboard/resumen/` | Dashboard — resumen | Autenticado |
| GET | `/api/v1/dashboard/evolucion-reportes/` | Dashboard — evolución de reportes | Autenticado |
| GET | `/api/v1/dashboard/mapa-calor/` | Dashboard — mapa de calor | Autenticado |
| GET | `/api/v1/dashboard/especies-afectadas/` | Dashboard — especies afectadas | Autenticado |
