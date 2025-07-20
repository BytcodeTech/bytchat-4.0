#!/usr/bin/env python3
"""
Script para actualizar la API key de Google y probar la conexión
"""

import os
import requests
import json

def test_google_api_key(api_key):
    """Prueba si una API key de Google funciona"""
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            models = response.json()
            print("✅ API Key válida!")
            print(f"📋 Modelos disponibles:")
            for model in models.get('models', [])[:5]:  # Mostrar primeros 5 modelos
                print(f"   - {model.get('name', 'Sin nombre')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error probando API key: {e}")
        return False

def update_env_file(new_api_key):
    """Actualiza el archivo .env con la nueva API key"""
    env_file = ".env"
    
    # Leer contenido actual
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Actualizar línea de GOOGLE_API_KEY
    updated = False
    for i, line in enumerate(lines):
        if line.startswith('GOOGLE_API_KEY='):
            lines[i] = f'GOOGLE_API_KEY={new_api_key}\n'
            updated = True
            break
    
    # Si no existe, agregarlo
    if not updated:
        lines.append(f'GOOGLE_API_KEY={new_api_key}\n')
    
    # Escribir archivo actualizado
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Archivo .env actualizado")

def main():
    print("🔑 Actualizador de API Key de Google")
    print("=" * 40)
    
    # Pedir nueva API key
    print("\n📝 Instrucciones:")
    print("1. Ve a: https://aistudio.google.com/app/apikey")
    print("2. Inicia sesión con tu cuenta Google")
    print("3. Click en 'Create API key'")
    print("4. Copia la API key generada")
    
    new_api_key = input("\n🔑 Pega tu nueva API key aquí: ").strip()
    
    if not new_api_key:
        print("❌ No se proporcionó API key")
        return
    
    # Probar la nueva API key
    print(f"\n🧪 Probando API key...")
    if test_google_api_key(new_api_key):
        # Actualizar archivo .env
        update_env_file(new_api_key)
        
        print("\n🔄 Ahora reinicia el contenedor web:")
        print("docker restart bychat_web")
        
        print("\n✅ ¡API key actualizada exitosamente!")
        print("Tu bot ya debería poder conectar con Google Gemini Flash")
    else:
        print("❌ La API key no funciona. Verifica que la copiaste correctamente.")

if __name__ == "__main__":
    main() 