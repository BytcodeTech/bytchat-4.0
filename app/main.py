from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import StreamingResponse

from . import auth, crud, models, schemas
from .database import engine, get_db
from .core.orchestrator import Orchestrator

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bytchat SaaS API",
    description="API para la plataforma multi-tenant de Bytchat.",
    version="1.0.0"
)

# --- Endpoints de Autenticación y Usuarios ---
@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# --- Endpoints para la Gestión de Bots (Protegidos) ---
@app.post("/bots/", response_model=schemas.Bot, tags=["Bots"])
def create_bot_for_user(bot: schemas.BotCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_user_bot(db=db, bot=bot, user_id=current_user.id)

@app.get("/bots/", response_model=List[schemas.Bot], tags=["Bots"])
def read_user_bots(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    bots = crud.get_bots_by_user(db, user_id=current_user.id)
    return bots

# --- Endpoint de Chat (Protegido y Funcional) ---
@app.post("/chat/{bot_id}", tags=["Chat"])
def handle_chat(
    bot_id: int, 
    query: str, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    bot = db.query(models.Bot).filter(models.Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    if bot.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este bot")

    bot_config = {"name": bot.name}
    orchestrator = Orchestrator(bot_config=bot_config)
    text_stream_generator = orchestrator.handle_query(user_id=str(current_user.id), query=query)
    
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

# --- Endpoint de Bienvenida ---
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a la API de Bytchat SaaS. Ve a /docs para ver la documentación interactiva."}
