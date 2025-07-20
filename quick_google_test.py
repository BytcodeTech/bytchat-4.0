#!/usr/bin/env python3

import requests
import json

# 1. Autenticarse
print("🔐 Autenticando...")
login_response = requests.post(
    "http://161.132.45.210:8001/token",
    data={"username": "gabi@gmail.com", "password": "gabi"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("✅ Autenticado")
    
    # 2. Enviar mensaje con endpoint autenticado
    print("💬 Enviando mensaje que registrará métricas de Google...")
    
    chat_response = requests.post(
        "http://161.132.45.210:8001/chat/2",
        json={"query": "Prueba para generar métricas de Google Gemini"},
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    if chat_response.status_code == 200:
        print("✅ ¡Mensaje enviado! Métricas de Google registradas")
        print(f"📝 Respuesta: {chat_response.text[:100]}...")
        print("\n🎯 Ahora las analytics mostrarán Google en lugar de DeepSeek")
    else:
        print(f"❌ Error: {chat_response.status_code} - {chat_response.text}")
else:
    print(f"❌ Error de autenticación: {login_response.text}") 