# Bytchat SaaS - Plataforma de Asistentes de IA v1.4.0

Bienvenido a la documentación de Bytchat, una plataforma como servicio (SaaS) diseñada para crear, gestionar y chatear con asistentes de IA personalizados. El proyecto está dividido en un backend robusto de FastAPI y un panel de control moderno construido con React.

## Arquitectura General

La plataforma está desplegada usando Docker y Docker Compose, e incluye los siguientes servicios:

  * **Nginx:** Proxy inverso que gestiona el tráfico público.
  * **FastAPI (Web):** El servidor principal de la API.
  * **PostgreSQL (DB):** Base de datos relacional para la persistencia de datos.
  * **Redis:** Broker de mensajería para tareas asíncronas.
  * **Celery (Worker):** Servicio para ejecutar tareas pesadas en segundo plano (como el entrenamiento de bots).
  * **React (Frontend):** Panel de control interactivo para la gestión de la plataforma.

## Estructura del Proyecto
/
├── app/                  # Directorio del backend de FastAPI
│   ├── core/
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── bytchat-panel/        # Directorio del frontend de React
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── store/
│       └── main.tsx
├── nginx/                # Configuración de Nginx
├── .env.example          # Ejemplo de archivo de variables de entorno
├── docker-compose.yml    # Orquestación de los servicios
└── README.md             # Esta documentación
## Guía de Instalación y Uso

### 1\. Configuración del Backend

El backend está completamente contenerizado, lo que simplifica su despliegue.

**Prerrequisitos:**

  - Tener Docker y Docker Compose (versión con el plugin, `docker compose`) instalados en el servidor.

**Pasos:**

1.  **Clona el repositorio** (si aplica).
2.  **Crea el archivo de entorno:** Copia el contenido de `.env.example` a un nuevo archivo llamado `.env` y rellena las variables, especialmente las credenciales de PostgreSQL.
    ```bash
    cp .env.example .env
    # Edita el archivo .env con tus valores
    ```
3.  **Levanta los servicios:** Desde la carpeta raíz del proyecto (`bytchat-4.0`), ejecuta el siguiente comando. La primera vez, construirá las imágenes de Docker.
    ```bash
    docker compose up -d --build
    ```
4.  **Verifica el estado:** Asegúrate de que todos los contenedores estén corriendo con:
    ```bash
    docker compose ps
    ```
    Todos los servicios (`web`, `db`, `nginx`, `worker`, `redis`) deberían mostrar el estado `running` o `up`.

Una vez levantado, el backend será accesible en `http://<IP_DEL_SERVIDOR>`. La documentación interactiva de la API estará disponible en `http://<IP_DEL_SERVIDOR>/docs`.

### 2\. Configuración del Frontend

El frontend utiliza un servidor de desarrollo de Vite.

**Prerrequisitos:**

  - Tener Node.js y npm instalados.

**Pasos:**

1.  **Navega a la carpeta del panel:**
    ```bash
    cd bytchat-panel
    ```
2.  **Instala las dependencias:**
    ```bash
    npm install
    ```
3.  **Inicia el servidor de desarrollo:** Para que sea accesible desde tu máquina local, usa el flag `--host`.
    ```bash
    npm run dev -- --host
    ```

El panel de control será accesible en `http://<IP_DEL_SERVIDOR>:5173`.

-----

## Documentación de la API

### Autenticación

La API utiliza un sistema de Tokens Bearer (OAuth2) para proteger los endpoints sensibles. El flujo es el siguiente:

1.  Registra un nuevo usuario con el endpoint `POST /users/`.
2.  Inicia sesión con ese usuario usando `POST /token` para obtener un `access_token`.
3.  Para todos los endpoints que requieran autenticación (marcados con un 🔒), debes incluir una cabecera (header) de la siguiente forma: `Authorization: Bearer TU_ACCESS_TOKEN_AQUI`

### Endpoints

A continuación se detallan los endpoints agrupados por funcionalidad.

#### 🟢 Authentication (`/token`)

  * **`POST /token`**
      * **Descripción:** Inicia sesión con un usuario y contraseña para obtener un token de acceso.
      * **Cuerpo de la Petición:** `application/x-www-form-urlencoded` con los campos `username` (que es el email) y `password`.
      * **Respuesta Exitosa (200):**
        ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }
        ```

#### 🟢 Users (`/users/`)

  * **`POST /users/`**
      * **Descripción:** Crea un nuevo usuario en la plataforma.
      * **Cuerpo de la Petición:**
        ```json
        {
          "email": "nuevo.usuario@ejemplo.com",
          "password": "una-clave-segura"
        }
        ```
      * **Respuesta Exitosa (200):** Devuelve el objeto del usuario creado (sin la contraseña).

#### 🟢 Bots (`/bots/`)

Endpoints protegidos para la gestión de los bots de un usuario. Requieren autenticación 🔒.

  * **`POST /bots/`**
      * **Descripción:** Crea un nuevo bot para el usuario autenticado.
      * **Cuerpo de la Petición:**
        ```json
        {
          "name": "Mi Nuevo Asistente",
          "description": "Un bot para pruebas.",
          "initial_configs": [
            {
              "task_type": "general",
              "provider": "google",
              "model_id": "gemini-1.5-flash-latest"
            }
          ]
        }
        ```
  * **`GET /bots/`**
      * **Descripción:** Devuelve una lista de todos los bots que pertenecen al usuario autenticado.
  * **`PUT /bots/{bot_id}`**
      * **Descripción:** Actualiza la configuración general de un bot (como su personalidad o "system prompt").
      * **Cuerpo de la Petición:**
        ```json
        {
          "system_prompt": "Ahora eres un robot pirata que habla como tal."
        }
        ```
  * **`POST /bots/{bot_id}/models/`**
      * **Descripción:** Añade un nuevo modelo de IA a la "caja de herramientas" de un bot específico.
      * **Cuerpo de la Petición:**
        ```json
        {
          "provider": "openai",
          "model_id": "gpt-4o",
          "task_type": "complex"
        }
        ```
  * **`POST /bots/{bot_id}/train`**
      * **Descripción:** Permite subir un documento de texto (`.txt`) para entrenar a un bot. El procesamiento se realiza en segundo plano.
      * **Cuerpo de la Petición:** `multipart/form-data` con un campo `file`.

#### 🟢 Chat (`/chat/`)

Endpoint protegido para interactuar con un bot. Requiere autenticación 🔒.

  * **`POST /chat/{bot_id}`**
      * **Descripción:** Envía una pregunta a un bot específico y recibe una respuesta en tiempo real (streaming).
      * **Cuerpo de la Petición:**
        ```json
        {
          "query": "¿Cuál es tu propósito?"
        }
        ```

#### 🟢 Root (`/`)

  * **`GET /`**
      * **Descripción:** Un endpoint simple para verificar que la API está en línea y obtener la versión actual. Devuelve un mensaje de bienvenida.

## Funcionalidades del Panel de Control (Frontend)

  - **Flujo de Autenticación Completo:**
      - Página de **Registro** (`/register`) para crear nuevos usuarios. (todavia no esta creada)
      - Página de **Login** (`/login`) para iniciar sesión.
  - **Rutas Protegidas:** El panel de control principal (`/`) es inaccesible para usuarios no autenticados y redirige al login.
  - **Gestión de Estado:** El token de autenticación se guarda de forma segura en el `localStorage` del navegador y se gestiona con `zustand`.
  - **Layout Principal:** Se ha implementado un layout base con una barra lateral de navegación y una cabecera, listo para albergar las futuras secciones del panel.

<!-- end list -->
