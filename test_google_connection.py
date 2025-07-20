#!/usr/bin/env python3
"""
Script para probar la conexión con Google Gemini después de actualizar la API key
"""

import requests
import os

def test_current_google_api():
    """Prueba la API key actual desde el archivo .env"""
    
    # Leer API key del archivo .env
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('GOOGLE_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
        else:
            print("❌ No se encontró GOOGLE_API_KEY en .env")
            return
    except FileNotFoundError:
        print("❌ Archivo .env no encontrado")
        return
    
    print(f"🔑 Probando API Key: {api_key[:20]}...")
    
    # Probar conexión con Google
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ ¡Conexión exitosa con Google!")
            
            # Buscar modelos Gemini Flash
            flash_models = []
            for model in models.get('models', []):
                name = model.get('name', '')
                if 'flash' in name.lower():
                    flash_models.append(name)
            
            if flash_models:
                print("🚀 Modelos Gemini Flash disponibles:")
                for model in flash_models[:3]:
                    print(f"   - {model}")
            
            print("\n✅ Tu bot ya puede usar Google Gemini Flash!")
            return True
            
        elif response.status_code == 400:
            print("❌ API Key inválida")
            print("💡 Genera una nueva en: https://aistudio.google.com/app/apikey")
            return False
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Probando conexión con Google Gemini")
    print("=" * 40)
    test_current_google_api() 