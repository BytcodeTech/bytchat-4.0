#!/usr/bin/env python3
"""
Solución rápida: Actualizar API key de Google directamente en la configuración
"""

import subprocess
import time
import os

def fix_google_api():
    print("🔧 Aplicando solución rápida para Google API...")
    
    # 1. Detener contenedor actual
    print("⏸️  Deteniendo contenedor actual...")
    subprocess.run(["docker", "stop", "bychat_web"], capture_output=True)
    subprocess.run(["docker", "rm", "bychat_web"], capture_output=True)
    
    # 2. Recrear con imagen original y API key desde variables de entorno
    print("🚀 Recreando contenedor con nueva configuración...")
    
    # Leer las API keys desde variables de entorno
    google_key = os.getenv("GOOGLE_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    if not all([google_key, openai_key, deepseek_key]):
        print("❌ Error: API keys no encontradas en variables de entorno")
        print("💡 Asegúrate de tener el archivo .env configurado")
        return
    
    cmd = [
        "docker", "run", "-d", 
        "--name", "bychat_web",
        "--restart", "unless-stopped",
        "-p", "8001:8000",
        "--network", "bytchat-40_default",
        "-e", f"GOOGLE_API_KEY={google_key}",
        "-e", f"OPENAI_API_KEY={openai_key}",
        "-e", f"DEEPSEEK_API_KEY={deepseek_key}",
        "-e", "DB_USER=postgres",
        "-e", "DB_PASSWORD=postgres", 
        "-e", "DB_NAME=bytchat",
        "-e", "POSTGRES_USER=postgres",
        "-e", "POSTGRES_PASSWORD=postgres",
        "-e", "POSTGRES_DB=bytchat",
        "bytchat-40-web:latest"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Contenedor creado exitosamente!")
        container_id = result.stdout.strip()
        print(f"🆔 ID del contenedor: {container_id[:12]}...")
        
        # 3. Esperar que inicie
        print("⏳ Esperando que el servidor inicie...")
        time.sleep(15)
        
        # 4. Verificar estado
        ps_result = subprocess.run(["docker", "ps", "--filter", "name=bychat_web"], 
                                 capture_output=True, text=True)
        
        if "bychat_web" in ps_result.stdout:
            print("✅ Contenedor ejecutándose correctamente!")
            
            # 5. Probar bot
            print("🧪 Probando bot...")
            test_result = subprocess.run([
                "curl", "-s", "-X", "POST", 
                "http://161.132.45.210:8001/chat/widget/2",
                "-H", "Content-Type: application/json",
                "-d", '{"userAnonId":"test_fix","query":"test google"}'
            ], capture_output=True, text=True, timeout=20)
            
            if "Google" not in test_result.stdout and "problema" not in test_result.stdout:
                print("🎉 ¡ÉXITO! El bot está funcionando con Google Gemini Flash")
                print("📝 Respuesta:", test_result.stdout[:100] + "...")
            else:
                print("⚠️  Respuesta del bot:", test_result.stdout[:100])
        else:
            print("❌ El contenedor no está ejecutándose")
            
    else:
        print("❌ Error creando contenedor:", result.stderr)

if __name__ == "__main__":
    fix_google_api() 