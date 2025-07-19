# Bytchat SaaS - Plataforma de Asistentes de IA v4.0

Bienvenido a la documentación de Bytchat, una plataforma como servicio (SaaS) diseñada para crear, gestionar y chatear con asistentes de IA personalizados. El proyecto está dividido en un backend robusto de FastAPI y un panel de control moderno construido con React.

## 🚀 Características Principales

- **Chatbots Inteligentes**: Crea asistentes de IA personalizados con múltiples modelos
- **Panel de Control Moderno**: Interfaz React intuitiva para gestionar bots
- **Sistema de Roles y Permisos**: Control granular de acceso con roles USER, ADMIN y SUPER_ADMIN
- **Panel de Administración**: Gestión completa de usuarios y aprobaciones
- **Gestión de Contraseñas**: Modal seguro para cambiar contraseña del usuario actual
- **Toggle de Aprobación**: Aprobar/desaprobar usuarios existentes (solo SUPER_ADMIN)
- **Integración Fácil**: Widget profesional para incrustar en cualquier web
- **Entrenamiento con Documentos**: Sube archivos para entrenar tus bots
- **API REST Completa**: Endpoints para integración personalizada
- **Despliegue Docker**: Configuración completa con Docker Compose

## 🏗️ Arquitectura

La plataforma está desplegada usando Docker y Docker Compose, e incluye los siguientes servicios:

- **Nginx**: Proxy inverso que gestiona el tráfico público
- **FastAPI (Web)**: El servidor principal de la API
- **PostgreSQL (DB)**: Base de datos relacional para la persistencia de datos
- **Redis**: Broker de mensajería para tareas asíncronas
- **Celery (Worker)**: Servicio para ejecutar tareas pesadas en segundo plano
- **React (Frontend)**: Panel de control interactivo para la gestión de la plataforma

## 🔐 Sistema de Roles y Permisos

### **Roles Disponibles**

1. **USER** (Usuario Regular)
   - Crear y gestionar sus propios bots
   - Entrenar bots con documentos
   - Usar el chat integrado
   - Acceso limitado al panel principal
   - Cambiar su propia contraseña

2. **ADMIN** (Administrador)
   - Todas las funcionalidades de USER
   - Acceso al Panel de Administración
   - Aprobar/rechazar usuarios nuevos
   - Gestionar usuarios de la plataforma
   - Ver métricas y estadísticas

3. **SUPER_ADMIN** (Super Administrador)
   - Todas las funcionalidades de ADMIN
   - Cambiar roles de usuarios
   - Aprobar/desaprobar usuarios existentes
   - Acceso completo a todas las funcionalidades
   - Gestión de configuración del sistema

### **Panel de Administración**

El panel de administración incluye:

- **Gestión de Usuarios**: Ver, aprobar, rechazar y gestionar usuarios
- **Usuarios Pendientes**: Lista de usuarios esperando aprobación
- **Estadísticas**: Métricas de uso y actividad
- **Gestión de Roles**: Cambiar roles de usuarios (solo SUPER_ADMIN)
- **Toggle de Aprobación**: Aprobar/desaprobar usuarios existentes (solo SUPER_ADMIN)
- **Gestión de Contraseñas**: Cambiar contraseña del usuario actual

## 📁 Estructura del Proyecto

```
/
├── app/                  # Backend FastAPI
│   ├── core/
│   ├── crud.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py          # Sistema de autenticación y permisos
│   └── config.py        # Configuración de la aplicación
├── bytchat-panel/        # Frontend React
│   ├── public/
│   └── src/
│       ├── components/
│       │   └── auth/
│       │       └── AdminRoute.tsx  # Protección de rutas
│       ├── pages/
│       │   └── AdminPage.tsx       # Panel de administración
│       ├── store/
│       │   └── authStore.ts        # Estado de autenticación
│       └── main.tsx
├── static/               # Archivos estáticos
│   ├── chat-widget.html
│   ├── bytchat-integration.js
│   └── demo-burbuja.html
├── nginx/                # Configuración de Nginx
├── .env.example          # Variables de entorno
├── docker-compose.yml    # Orquestación de servicios
├── migrate_users.py      # Script de migración y creación de super admin
└── README.md             # Esta documentación
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose (versión con plugin)
- Node.js y npm (para desarrollo del frontend)

### 1. Configuración del Backend

1. **Clona el repositorio** (si aplica)
2. **Crea el archivo de entorno:**
   ```bash
   cp .env.example .env
   # Edita el archivo .env con tus valores
   ```
3. **Levanta los servicios:**
   ```bash
   docker-compose up -d --build
   ```
4. **Ejecuta la migración inicial:**
   ```bash
   docker-compose exec web python migrate_users.py
   ```
5. **Verifica el estado:**
   ```bash
   docker-compose ps
   ```

Una vez levantado, el backend será accesible en `http://<IP_DEL_SERVIDOR>`. La documentación interactiva de la API estará disponible en `http://<IP_DEL_SERVIDOR>/docs`.

### 2. Configuración del Frontend

1. **Navega a la carpeta del panel:**
   ```bash
   cd bytchat-panel
   ```
2. **Instala las dependencias:**
   ```bash
   npm install
   ```
3. **Inicia el servidor de desarrollo:**
   ```bash
   npm run dev -- --host
   ```

El panel de control será accesible en `http://<IP_DEL_SERVIDOR>:5175`.

## 🔐 Configuración de Variables de Entorno

Crea un archivo `.env` con las siguientes variables:

```env
# Variables de Base de Datos PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=bytchat

# Variables para la aplicación
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=bytchat

# Variables para el Super Administrador
SUPER_ADMIN_EMAIL=admin@bytcode.tech
SUPER_ADMIN_PASSWORD=admin123

# API Keys
GOOGLE_API_KEY=tu_google_api_key
OPENAI_API_KEY=tu_openai_api_key
DEEPSEEK_API_KEY=tu_deepseek_api_key

# Variables adicionales
SECRET_KEY=un_secreto_muy_secreto_para_el_token
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://redis:6379
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379
DATABASE_URL=postgresql://postgres:postgres@db/bytchat
```

## 📚 Documentación de la API

### Autenticación

La API utiliza un sistema de Tokens Bearer (OAuth2) para proteger los endpoints sensibles:

1. Registra un nuevo usuario con `POST /users/`
2. Inicia sesión con `POST /token` para obtener un `access_token`
3. Incluye la cabecera: `Authorization: Bearer TU_ACCESS_TOKEN_AQUI`

### Endpoints Principales

#### 🔐 Authentication (`/token`)
- **`POST /token`**: Inicia sesión y obtiene token de acceso

#### 👥 Users (`/users/`)
- **`POST /users/`**: Crea un nuevo usuario
- **`GET /users/me/`**: Obtiene información del usuario actual
- **`PUT /users/me/password/`**: Cambia la contraseña del usuario actual

#### 🤖 Bots (`/bots/`) - Requiere autenticación 🔒
- **`POST /bots/`**: Crea un nuevo bot
- **`GET /bots/`**: Lista todos los bots del usuario
- **`PUT /bots/{bot_id}`**: Actualiza un bot
- **`DELETE /bots/{bot_id}`**: Elimina un bot
- **`POST /bots/{bot_id}/models/`**: Añade modelo de IA
- **`DELETE /bots/{bot_id}/models/{model_config_id}`**: Elimina modelo
- **`POST /bots/{bot_id}/train`**: Entrena bot con documento

#### 💬 Chat (`/chat/`) - Requiere autenticación 🔒
- **`POST /chat/{bot_id}`**: Envía mensaje y recibe respuesta en streaming

#### 🛡️ Admin (`/admin/`) - Requiere rol ADMIN 🔒
- **`GET /admin/users/`**: Lista todos los usuarios
- **`GET /admin/users/pending/`**: Lista usuarios pendientes de aprobación
- **`POST /admin/users/{user_id}/approve/`**: Aprueba un usuario
- **`POST /admin/users/{user_id}/reject/`**: Rechaza un usuario
- **`PUT /admin/users/{user_id}/status/`**: Actualiza estado de usuario

#### 👑 Super Admin (`/admin/`) - Requiere rol SUPER_ADMIN 🔒
- **`POST /admin/users/{user_id}/role/`**: Cambia rol de usuario
- **`POST /admin/users/{user_id}/toggle-approval/`**: Cambia estado de aprobación de usuario (aprobar/desaprobar)

#### 🏠 Root (`/`)
- **`GET /`**: Verifica que la API está en línea

## 🎛️ Panel de Control (Frontend)

### Funcionalidades Principales

- **🔐 Autenticación Completa**: Login y registro con gestión de estado
- **🛡️ Rutas Protegidas**: Panel inaccesible para usuarios no autenticados
- **👑 Sistema de Roles**: Diferentes niveles de acceso según el rol
- **🔒 Gestión de Contraseñas**: Modal seguro para cambiar contraseña del usuario actual
- **🤖 Gestión de Bots (CRUD)**:
  - Crear bots con formulario modal
  - Listar bots en cuadrícula moderna
  - Editar nombre, descripción e instrucciones
  - Eliminar bots con confirmación
- **🛠️ Toolbox de Modelos**: Gestionar modelos de IA por bot
- **📊 Entrenamiento**: Subir documentos para entrenar bots
- **💬 Chat Integrado**: Probar bots directamente desde el panel
- **🎨 Integración de Widget**: Generar código para incrustar chat
- **🔔 Notificaciones**: Feedback visual para todas las operaciones

### Panel de Administración

- **👥 Gestión de Usuarios**: Ver, aprobar y gestionar usuarios
- **⏳ Usuarios Pendientes**: Lista de usuarios esperando aprobación
- **📊 Estadísticas**: Métricas de uso y actividad
- **🔐 Gestión de Roles**: Cambiar roles de usuarios (solo SUPER_ADMIN)
- **🔄 Toggle de Aprobación**: Aprobar/desaprobar usuarios existentes (solo SUPER_ADMIN)
- **🔒 Cambio de Contraseña**: Modal seguro para cambiar contraseña del usuario actual

### Vista Previa Interactiva del Widget

El panel incluye una **vista previa interactiva** que simula la experiencia real del widget:

- **Estado inicial**: Solo burbuja flotante
- **Interactividad**: Clic en burbuja abre el chat
- **Minimización**: Clic en X vuelve a la burbuja
- **Animaciones suaves**: Transiciones fluidas entre estados
- **Personalización en tiempo real**: Colores, logo, nombre y mensaje

## 🌐 Integración del Widget

### Integración Fácil (Recomendada)

Para añadir el chat profesional de Bytchat a tu web, solo copia y pega este código antes de la etiqueta `</body>`:

```html
<script>
  window.bytchatConfig = {
    botId: "AQUÍ_SU_ID", // Obligatorio
    color: "#14305a",    // Opcional
    logo: "URL_DEL_LOGO",// Opcional
    nombre: "ChatBot",   // Opcional
    mensaje: "¡Hola! ¿En qué puedo ayudarte?" // Opcional
  };
</script>
<script src="https://bytcode.tech/static/bytchat-integration.js"></script>
```

### Características del Widget

- **Burbuja Profesional**: Aparece como burbuja flotante
- **Apertura/Cierre Suave**: Animaciones profesionales
- **Personalización**: Color, logo, nombre y mensaje
- **Responsive**: Se adapta a cualquier dispositivo
- **Sin HTML Extra**: El script crea todo automáticamente

### Integración Avanzada

Para control total del widget, puedes usar el sistema de `postMessage`:

```html
<div id="bytchat-box" style="position: fixed; bottom: 20px; right: 20px; width: 350px; height: 500px; z-index: 1000;">
  <iframe 
    src="https://bytcode.tech/static/chat-widget.html?id=TU_BOT_ID&color=%2314305a&bg=%23f5f5f5&mensaje=%C2%A1Hola!%20%C2%BFEn%20qu%C3%A9%20puedo%20ayudarte%3F&logo=URL_DEL_LOGO&nombre=ChatBot" 
    style="width: 100%; height: 100%; border: none; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"
    title="Chat Widget"
    allow="microphone"
  ></iframe>
</div>

<script>
window.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'bytchat-state') {
    const box = document.getElementById('bytchat-box');
    if (box) {
      box.style.width = event.data.width + 'px';
      box.style.height = event.data.height + 'px';
      box.style.display = (event.data.state === 'open' || event.data.state === 'close') ? 'block' : 'none';
    }
  }
});
</script>
```

## 🔧 Migración y Actualizaciones

### Migración Inicial

Para configurar el sistema de roles en una instalación existente:

```bash
# Ejecutar el script de migración
docker-compose exec web python migrate_users.py
```

Este script:
- ✅ Añade la columna `role` a la tabla `users`
- ✅ Actualiza usuarios existentes con rol `USER`
- ✅ Crea un super administrador por defecto

### Credenciales por Defecto

Después de la migración, se crea automáticamente un super administrador:

- **Email**: `admin@bytcode.tech`
- **Password**: `admin123`

**⚠️ IMPORTANTE**: Cambia la contraseña después del primer login.

## 📖 Documentación Adicional

- **Integración Completa**: `/static/INTEGRACION_WIDGET.html`
- **Demo del Widget**: `/static/demo-burbuja.html`
- **API Docs**: `http://<IP_DEL_SERVIDOR>/docs`

## 🔒 Seguridad

### Características de Seguridad

- **Autenticación JWT**: Tokens seguros con expiración
- **Sistema de Roles**: Control granular de acceso
- **Aprobación Manual**: Usuarios requieren aprobación de administradores
- **Protección de Rutas**: Frontend y backend validan permisos
- **Encriptación de Contraseñas**: Hashing con bcrypt
- **Gestión de Contraseñas**: Validación de contraseña actual antes de cambiar
- **Toggle de Aprobación**: Control granular sobre el estado de aprobación de usuarios

### Mejores Prácticas

1. **Cambiar credenciales por defecto** después de la instalación
2. **Usar HTTPS** en producción
3. **Configurar firewall** para proteger puertos sensibles
4. **Hacer backups regulares** de la base de datos
5. **Monitorear logs** para detectar actividad sospechosa

## 🤝 Soporte

Si tienes dudas o necesitas soporte, contacta a nuestro equipo técnico.

---

**Bytchat - Plataforma de Asistentes de IA v4.0**