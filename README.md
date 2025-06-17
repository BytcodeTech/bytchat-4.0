# Bytchat 4.0

Bytchat 4.0 es una plataforma de chatbot avanzada y modular, diseñada para ofrecer conversaciones inteligentes y contextuales. La aplicación integra un sistema de **Generación Aumentada por Recuperación (RAG)** para responder preguntas basadas en una base de conocimiento documental, y cuenta con un sistema de enrutamiento capaz de conectarse a múltiples proveedores de Modelos de Lenguaje Grandes (LLM) como Google, OpenAI y DeepSeek.

## ✨ Características Principales

* **Interfaz de Chat Interactiva**: Un widget de chat moderno y responsivo construido con HTML, CSS y JavaScript.
* **Backend Asíncrono de Alto Rendimiento**: Construido con **FastAPI**, garantiza respuestas rápidas y eficientes.
* **Generación Aumentada por Recuperación (RAG)**: El chatbot puede consultar una base de datos vectorial (creada con FAISS) para encontrar información relevante en documentos locales y usarla como contexto para generar respuestas precisas.
* **Soporte Multi-LLM**: Arquitectura de conectores que permite integrar y utilizar fácilmente diferentes modelos de lenguaje de proveedores como Google (Gemini), OpenAI (GPT) y DeepSeek.
* **Respuestas en Tiempo Real (Streaming)**: Las respuestas del bot se transmiten palabra por palabra, mejorando significativamente la experiencia del usuario.
* **Procesamiento de Datos Personalizado**: Incluye un script (`indexer.py`) para procesar tus propios documentos de texto, convertirlos en vectores y construir la base de conocimiento para el sistema RAG.

## 🚀 Arquitectura del Proyecto

El proyecto sigue una arquitectura modular y desacoplada que separa las responsabilidades principales:

1.  **Frontend (`index.html`, `static/script.js`)**: La capa de presentación con la que interactúa el usuario. Se comunica con el backend a través de una API REST.
2.  **Backend (`app.py`)**: El servidor web de FastAPI que expone el endpoint `/chat` y gestiona el ciclo de vida de la aplicación.
3.  **Orquestador (`core/orchestrator.py`)**: Es el cerebro de la aplicación. Recibe las consultas, utiliza el RAG para obtener contexto, consulta al enrutador de modelos y delega la generación de la respuesta al conector correspondiente.
4.  **Sistema RAG (`core/rag_retriever.py`)**: Se encarga de convertir la pregunta del usuario en un vector, buscar en el índice FAISS los documentos más relevantes y devolver el contexto al orquestador.
5.  **Conectores (`connectors/`)**: Módulos individuales que encapsulan la lógica para comunicarse con las APIs de los diferentes proveedores de LLM (Google, OpenAI, etc.).
6.  **Indexer (`indexer.py`)**: Herramienta offline para procesar documentos de texto (`.txt`) y crear la base de datos vectorial que utiliza el sistema RAG.

## 🛠️ Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### Prerrequisitos

* Python 3.8+
* pip (gestor de paquetes de Python)

### 1. Clona el Repositorio

```bash
git clone [https://github.com/tu-usuario/bytchat-4.0.git](https://github.com/tu-usuario/bytchat-4.0.git)
cd bytchcat-4.0
