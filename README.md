Documentación de la API Bytchat SaaS v1.4.0
Bienvenido a la documentación de la API para la plataforma Bytchat. Esta API RESTful permite gestionar usuarios, crear y configurar bots de IA personalizados con su propia base de conocimiento, y chatear con ellos.
Arquitectura
La plataforma está desplegada usando Docker y Docker Compose, e incluye los siguientes servicios:
Nginx: Proxy inverso que gestiona el tráfico público.
FastAPI (Web): El servidor principal de la API.
PostgreSQL (DB): Base de datos relacional para la persistencia de datos.
Redis: Broker de mensajería para tareas asíncronas.
Celery (Worker): Servicio para ejecutar tareas pesadas en segundo plano (como el entrenamiento de bots).
Autenticación
La API utiliza un sistema de Tokens Bearer (OAuth2) para proteger los endpoints sensibles. El flujo es el siguiente:
Registra un nuevo usuario con el endpoint POST /users/.
Inicia sesión con ese usuario usando POST /token para obtener un access_token.
Para todos los endpoints que requieran autenticación (marcados con un 🔒), debes incluir una cabecera (header) de la siguiente forma: Authorization: Bearer TU_ACCESS_TOKEN_AQUI
Endpoints de la API
A continuación se detallan los endpoints agrupados por funcionalidad.
🟢 Authentication (/token)
Endpoints para gestionar el inicio de sesión.
POST /token
Descripción: Inicia sesión con un usuario y contraseña para obtener un token de acceso.
Cuerpo de la Petición: application/x-www-form-urlencoded con los campos username (que es el email) y password.
Respuesta Exitosa (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}


🟢 Users (/users/)
Endpoint para la gestión de usuarios.
POST /users/
Descripción: Crea un nuevo usuario en la plataforma.
Cuerpo de la Petición:
{
  "email": "nuevo.usuario@ejemplo.com",
  "password": "una-clave-segura"
}


Respuesta Exitosa (200): Devuelve el objeto del usuario creado (sin la contraseña).
🟢 Bots (/bots/)
Endpoints protegidos para la gestión de los bots de un usuario. Requieren autenticación 🔒.
POST /bots/
Descripción: Crea un nuevo bot para el usuario autenticado.
Cuerpo de la Petición:
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


GET /bots/
Descripción: Devuelve una lista de todos los bots que pertenecen al usuario autenticado.
PUT /bots/{bot_id}
Descripción: Actualiza la configuración general de un bot (como su personalidad o "system prompt").
Cuerpo de la Petición:
{
  "system_prompt": "Ahora eres un robot pirata que habla como tal."
}


POST /bots/{bot_id}/models/
Descripción: Añade un nuevo modelo de IA a la "caja de herramientas" de un bot específico.
Cuerpo de la Petición:
{
  "provider": "openai",
  "model_id": "gpt-4o",
  "task_type": "complex"
}


POST /bots/{bot_id}/train
Descripción: Permite subir un documento de texto (.txt) para entrenar a un bot. El procesamiento se realiza en segundo plano.
Cuerpo de la Petición: multipart/form-data con un campo file.
🟢 Chat (/chat/)
Endpoint protegido para interactuar con un bot. Requiere autenticación 🔒.
POST /chat/{bot_id}
Descripción: Envía una pregunta a un bot específico y recibe una respuesta en tiempo real (streaming).
Parámetros:
bot_id (en la URL): El ID del bot con el que se quiere chatear.
query (en la URL): La pregunta del usuario.
🟢 Root (/)
Endpoint de bienvenida.
GET /
Descripción: Un endpoint simple para verificar que la API está en línea y obtener la versión actual. Devuelve un mensaje de bienvenida.