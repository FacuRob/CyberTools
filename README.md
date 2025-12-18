# 🛡️ Ciberseguridad Web con Python: 🐍 CyberTools 

# 🛡️ Ciberseguridad Web con Python: 🐍 CyberTools Pro 🐍

<div align="center">
  
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Google Fonts](https://img.shields.io/badge/Google%20Fonts-4285F4?style=for-the-badge&logo=google-fonts&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Segurity](https://img.shields.io/badge/Security-4EA94B?style=for-the-badge&logo=securityscorecard&logoColor=white)
![Networking](https://img.shields.io/badge/Networking-00599C?style=for-the-badge&logo=cisco&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

</div>

¡Repositorio de Ciberseguridad con Python! 🐍
Este proyecto presenta una plataforma web interactiva diseñada para demostrar y utilizar diversas herramientas de ciberseguridad desarrolladas en Python. 
La interfaz está diseñada con un estilo de terminal, ofreciendo una experiencia visualmente atractiva e intuitiva.

## ✨ Características Principales

- **🔍 Escaneo de Puertos Optimizado**: Análisis paralelo con caché DNS, timeouts dinámicos y detección inteligente de servicios (100 hilos concurrentes)
- **🔐 Generador de Contraseñas Avanzado**: Generación aleatoria o basada en frases memorables con opciones personalizables
- **📄 Analizador de Metadatos**: Extracción de información oculta de archivos PDF, Word, Excel, imágenes y más (EXIF, GPS, autor, etc.)

## 🌐 Demo en línea activa
Puedes probar la aplicación directamente en:  
🔗 [CyberTools](https://cybertools-3f82.onrender.com/)

## 🛠️ Tecnologías Utilizadas

**Backend:**
  - Python 3.x
  - Flask: Microframework web para el manejo de rutas y APIs.

**Frontend:**
  - HTML5
  - CSS3
  - JavaScript: Para la interacción y la comunicación con el Backend.
  - Bootstrap 5: Para el diseño responsivo.
  - Bootstrap Icons: Para el uso de iconos.
  - Google Fonts: Para el uso de fuentes.

**Despliegue:**
  - Render: Plataforma cloud para despliegue de aplicaciones web.

## 🚀 Configuración Inicial

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/FacuRob/CyberTools

   cd CyberTools

2. **Instalar todas las dependencias**
   ```bash
   pip install -r requirements.txt

   Esto instalará automáticamente:
   - Flask (framework web)
   - Pillow (análisis de imágenes y EXIF)
   - PyPDF2 (análisis de PDF)
   - python-docx (análisis de Word)
   - openpyxl (análisis de Excel)
   - Y otras dependencias necesarias

   cd nombre-del-repositorio

2. **Instalación de Microframework de Python**
   ```bash
   pip install Flask

3. **Ejecución del Sistema**
   ```bash
   python app.py

   El servidor se ejecutará en http://127.0.0.1:5000

4. **Nota*: Al Ejecutar veras algo similar**
   ```bash
   * Serving Flask app 'app'
   * Debug mode: on
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
   * Running on http://127.0.0.1:5000
   * Running on http://192.168.100.37:5000
   Press CTRL+C to quit

## 🚀 Despliegue en Render

1. **Crear una cuenta en Render**
2. **Haz click en "New" seguido de "Web Service"**
3. **Conectar tu repositorio de GitHub, de no aparecer puedes colocar el link del repositorio**
4. **Configurar:**
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
5. **Seleccionar el plan gratuito**
6. **¡Desplegar!**

## 📫 Contacto

Si deseas intercambiar ideas sobre Ciberseguridad, contactame:
- Portfolio: [FacuRob.porfolio](https://facurobportfolio.netlify.app/)
- GitHub: [FacuRob](https://github.com/FacuRob)
- LinkedIn: [Facundo Robles](https://www.linkedin.com/in/frobles-dev/)
- TryHackMe: [Facundo Robles](https://tryhackme.com/p/roblesfacundo7)
