
# Usa una imagen base oficial de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de dependencias
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copia el resto del código de tu aplicación al contenedor
COPY . .

# Expone el puerto que usará la aplicación
EXPOSE 8000
