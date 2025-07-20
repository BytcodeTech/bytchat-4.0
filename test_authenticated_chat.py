#!/usr/bin/env python3
"""
Script de prueba para demostrar el endpoint de chat autenticado que registra métricas
"""

import requests
import json

# Configuración del servidor
BASE_URL = "http://161.132.45.210:8001"

def test_authenticated_chat():
    """Prueba el endpoint de chat autenticado"""
    
    # 1. Obtener token de autenticación
    login_data = {
        "username": "gabi@gmail.com",  # Email del usuario
        "password": "gabi"             # Contraseña correcta
    }
    
    print("🔐 Intentando autenticación...")
    login_response = requests.post(
        f"{BASE_URL}/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error de autenticación: {login_response.status_code}")
        print(f"Respuesta: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print("✅ Autenticación exitosa!")
    
    # 2. Obtener lista de bots del usuario
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n📋 Obteniendo bots del usuario...")
    bots_response = requests.get(f"{BASE_URL}/bots/", headers=headers)
    
    if bots_response.status_code != 200:
        print(f"❌ Error obteniendo bots: {bots_response.status_code}")
        return
    
    bots = bots_response.json()
    if not bots:
        print("❌ No se encontraron bots para este usuario")
        return
    
    bot_id = bots[0]["id"]
    bot_name = bots[0]["name"]
    print(f"✅ Bot encontrado: {bot_name} (ID: {bot_id})")
    
    # 3. Enviar mensaje usando el endpoint autenticado
    chat_data = {
        "query": "Hola, esta es una prueba del sistema de métricas."
    }
    
    print(f"\n💬 Enviando mensaje al bot {bot_id}...")
    chat_response = requests.post(
        f"{BASE_URL}/chat/{bot_id}",
        json=chat_data,
        headers={
            **headers,
            "Content-Type": "application/json"
        }
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Error en chat: {chat_response.status_code}")
        print(f"Respuesta: {chat_response.text}")
        return
    
    print("✅ Mensaje enviado exitosamente!")
    print(f"📝 Respuesta del bot: {chat_response.text[:100]}...")
    
    # 4. Verificar analytics del bot
    print(f"\n📊 Verificando analytics del bot {bot_id}...")
    analytics_response = requests.get(
        f"{BASE_URL}/bots/{bot_id}/analytics",
        headers=headers
    )
    
    if analytics_response.status_code == 200:
        analytics = analytics_response.json()
        print("✅ Analytics obtenidas:")
        print(f"   📈 Total mensajes: {analytics['total_messages']}")
        print(f"   🔤 Total tokens: {analytics['total_tokens']}")
        print(f"   💰 Costo total: ${analytics['total_cost_cents']/100:.2f}")
        print(f"   📅 Uso diario: {analytics['daily_usage']}")
    else:
        print(f"❌ Error obteniendo analytics: {analytics_response.status_code}")

def test_user_summary():
    """Prueba el endpoint de resumen de analytics del usuario"""
    
    # Obtener token (mismo proceso que arriba)
    login_data = {
        "username": "gabi@gmail.com",
        "password": "gabi"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Obtener resumen de analytics
    print("\n📊 Obteniendo resumen de analytics del usuario...")
    summary_response = requests.get(
        f"{BASE_URL}/user/analytics/summary",
        headers=headers
    )
    
    if summary_response.status_code == 200:
        summary = summary_response.json()
        print("✅ Resumen obtenido:")
        print(f"   🤖 Total bots: {summary['total_bots']}")
        print(f"   💬 Total mensajes: {summary['total_messages']}")
        print(f"   🔤 Total tokens: {summary['total_tokens']}")
        print(f"   💰 Costo total: ${summary['total_cost_cents']/100:.2f}")
    else:
        print(f"❌ Error obteniendo resumen: {summary_response.status_code}")

if __name__ == "__main__":
    print("🧪 Probando sistema de métricas de Bytchat")
    print("=" * 50)
    
    try:
        test_authenticated_chat()
        test_user_summary()
        
        print("\n" + "=" * 50)
        print("✅ Pruebas completadas!")
        print("\n📖 Instrucciones para el usuario:")
        print("1. Usa el endpoint POST /chat/{bot_id} para chat autenticado")
        print("2. Usa GET /bots/{bot_id}/analytics para ver métricas del bot")
        print("3. Usa GET /user/analytics/summary para resumen general")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}") 