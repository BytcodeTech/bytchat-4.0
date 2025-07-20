#!/usr/bin/env python3
"""
Script para probar el chat autenticado que registra métricas de Google correctamente
"""

import requests
import json

BASE_URL = "http://161.132.45.210:8001"

def test_authenticated_google_metrics():
    """Prueba el chat autenticado para generar métricas de Google"""
    
    # 1. Autenticarse
    print("🔐 Autenticando...")
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "gabi@gmail.com", "password": "gabi"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Error de autenticación: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Autenticado exitosamente")
    
    # 2. Enviar mensaje usando endpoint autenticado (registra métricas)
    print("\n💬 Enviando mensaje con endpoint autenticado...")
    chat_response = requests.post(
        f"{BASE_URL}/chat/2",  # Endpoint autenticado
        json={"query": "Hola, esta es una prueba para registrar métricas de Google Gemini"},
        headers={**headers, "Content-Type": "application/json"}
    )
    
    if chat_response.status_code == 200:
        print("✅ Mensaje enviado exitosamente!")
        print(f"📝 Respuesta: {chat_response.text[:100]}...")
    else:
        print(f"❌ Error: {chat_response.status_code} - {chat_response.text}")
        return
    
    # 3. Esperar un poco para que se procesen las métricas
    import time
    print("\n⏳ Esperando que se registren las métricas...")
    time.sleep(5)
    
    # 4. Verificar analytics
    print("\n📊 Verificando analytics actualizadas...")
    analytics_response = requests.get(
        f"{BASE_URL}/bots/2/analytics",
        headers=headers
    )
    
    if analytics_response.status_code == 200:
        analytics = analytics_response.json()
        print("✅ Analytics obtenidas:")
        print(f"   📈 Total mensajes: {analytics['total_messages']}")
        print(f"   🔤 Total tokens: {analytics['total_tokens']}")
        print(f"   💰 Costo total: ${analytics['total_cost_cents']/100:.4f}")
        print(f"   📅 Uso diario: {analytics['daily_usage']}")
    else:
        print(f"❌ Error obteniendo analytics: {analytics_response.status_code}")

if __name__ == "__main__":
    print("🧪 Probando chat autenticado para registrar métricas de Google")
    print("=" * 60)
    test_authenticated_google_metrics()
    
    print("\n" + "=" * 60)
    print("✅ Prueba completada!")
    print("\n📖 Para ver métricas de Google en el dashboard:")
    print("1. Usa el endpoint POST /chat/2 (autenticado)")
    print("2. NO uses /chat/widget/2 (solo para widgets públicos)")
    print("3. Las métricas aparecerán como 'google' en lugar de 'deepseek'") 