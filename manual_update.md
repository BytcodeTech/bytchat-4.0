# Manual para actualizar Google API Key

## Pasos rápidos:

1. **Obtener nueva API Key:**
   - Ve a: https://aistudio.google.com/app/apikey
   - Click en "Create API key"
   - Copia la API key generada

2. **Actualizar archivo .env:**
   ```bash
   cd /root/bytchat-4.0
   nano .env
   ```
   
   Cambiar la línea:
   ```
   GOOGLE_API_KEY=TU_NUEVA_API_KEY_AQUI
   ```

3. **Reiniciar servidor:**
   ```bash
   docker restart bychat_web
   ```

4. **Probar el bot:**
   - El bot ahora debería conectar con Google Gemini Flash
   - Las métricas se seguirán registrando correctamente

## ¿Por qué falló la anterior?
La API key anterior era inválida o expirada. Las API keys de Google AI Studio son gratuitas pero pueden tener límites de tiempo o uso.

## Beneficios de Gemini Flash:
- ✅ Más rápido que DeepSeek
- ✅ Mejor calidad de respuestas
- ✅ Gratis (con límites generosos)
- ✅ Compatible con el sistema de métricas 