from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from core.orchestrator import Orchestrator

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Evento de Startup: Cargando el Orchestrator...")
    ml_models["orchestrator"] = Orchestrator()
    print("Evento de Startup: Orchestrator y todos los modelos cargados.")
    yield
    print("Evento de Shutdown: Limpiando modelos...")
    ml_models.clear()

app = FastAPI(title="Bytcode Chatbot", version="1.5.1", lifespan=lifespan)

class ChatRequest(BaseModel):
    user_id: str
    query: str

@app.post("/chat")
def handle_chat(request: ChatRequest):
    text_stream_generator = ml_models["orchestrator"].handle_query(
        user_id=request.user_id,
        query=request.query
    )
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    # Asumiendo que index.html está en la raíz del proyecto
    return "index.html"