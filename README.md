# Documentación de la API Bytchat SaaS v1.2.1

Bienvenido a la documentación de la API para la plataforma Bytchat. Esta API permite gestionar usuarios, crear y configurar bots de IA personalizados, y chatear con ellos.

## Autenticación

La API utiliza un sistema de **Tokens Bearer (OAuth2)** para proteger los endpoints sensibles. El flujo es el siguiente:
1.  Registra un nuevo usuario con el endpoint `POST /users/`.
2.  Inicia sesión con ese usuario usando `POST /token` para obtener un `access_token`.
3.  Para todos los endpoints que requieran autenticación, debes incluir una cabecera (header) de la siguiente forma: `Authorization: Bearer TU_ACCESS_TOKEN_AQUI`

## Endpoints de la API

A continuación se detallan los endpoints agrupados por funcionalidad.

---

### 🟢 Authentication (`/token`)

Endpoints para gestionar el inicio de sesión.

#### `POST /token`
- **Descripción:** Inicia sesión con un usuario y contraseña para obtener un token de acceso.
- **Cuerpo de la Petición:** `application/x-www-form-urlencoded` con los campos `username` (que es el email) y `password`.
- **Respuesta Exitosa (200):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

---

### 🟢 Users (`/users/`)

Endpoint para la gestión de usuarios.

#### `POST /users/`
- **Descripción:** Crea un nuevo usuario en la plataforma.
- **Cuerpo de la Petición:**
  ```json
  {
    "email": "nuevo.usuario@ejemplo.com",
    "password": "una-clave-segura"
  }
  ```
- **Respuesta Exitosa (200):** Devuelve el objeto del usuario creado (sin la contraseña).
  ```json
  {
    "email": "nuevo.usuario@ejemplo.com",
    "id": 1,
    "is_active": true,
    "bots": []
  }
  ```

---

### 🟢 Bots (`/bots/`)

Endpoints protegidos para la gestión de los bots de un usuario. Requieren autenticación.

#### `POST /bots/`
- **Descripción:** Crea un nuevo bot para el usuario autenticado.
- **Cuerpo de la Petición:**
  ```json
  {
    "name": "Mi Nuevo Asistente",
    "description": "Un bot para pruebas."
  }
  ```

#### `GET /bots/`
- **Descripción:** Devuelve una lista de todos los bots que pertenecen al usuario autenticado.

#### `PUT /bots/{bot_id}`
- **Descripción:** Actualiza la configuración general de un bot (como su personalidad o "system prompt").
- **Cuerpo de la Petición:**
  ```json
  {
    "system_prompt": "Ahora eres un robot pirata que habla como tal."
  }
  ```

#### `POST /bots/{bot_id}/models/`
- **Descripción:** Añade un nuevo modelo de IA a la "caja de herramientas" de un bot específico.
- **Cuerpo de la Petición:**
  ```json
  {
    "provider": "openai",
    "model_id": "gpt-4o",
    "task_type": "complex"
  }
  ```

---

### 🟢 Chat (`/chat/`)

Endpoint protegido para interactuar con un bot.

#### `POST /chat/{bot_id}`
- **Descripción:** Envía una pregunta a un bot específico y recibe una respuesta en tiempo real (streaming).
- **Parámetros:**
    - `bot_id` (en la URL): El ID del bot con el que se quiere chatear.
    - `query` (en la URL): La pregunta del usuario.

---

### 🟢 Root (`/`)

Endpoint de bienvenida.

#### `GET /`
- **Descripción:** Un endpoint simple para verificar que la API está en línea. Devuelve un mensaje de bienvenida.

