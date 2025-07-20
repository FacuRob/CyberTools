import os
from flask import Flask, render_template, request, jsonify
from typing import Optional, Dict, Any
from typing import List
from components.scan_website_ports import scan_website_ports
from components.generate_strong_password import generate_strong_password

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración básica
app.config['JSON_SORT_KEYS'] = False  # Para mantener el orden en las respuestas JSON
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Límite de 16MB para requests

# Ruta principal - Sirve el frontend HTML
@app.route('/')
def index():
    return render_template('index.html')

# Colocación de icono.
@app.route('/images/logo.ico')
def favicon():
    return app.send_static_file('images/logo.ico')

# API para escaneo de puertos
@app.route('/api/scan_ports', methods=['POST'])
def api_scan_ports():
    try:
        # Verificar si es JSON
        if not request.is_json:
            return jsonify({"status": "error", "message": "Se esperaba JSON"}), 400

        data = request.get_json()
        target = data.get('target')
        
        # Validación mínima del target
        if not target or not isinstance(target, str):
            return jsonify({"status": "error", "message": "Target inválido"}), 400

        # Obtener puertos (ahora con valor por defecto)
        custom_ports = data.get('ports', [80, 443, 22, 21, 8080])  # Puertos comunes por defecto

        # Validar puertos
        if not isinstance(custom_ports, list):
            return jsonify({"status": "error", "message": "Los puertos deben ser una lista"}), 400

        # Escanear
        scan_result = scan_website_ports(target, custom_ports)
        
        # Manejar errores del escaneo
        if "error" in scan_result:
            return jsonify({"status": "error", "message": scan_result["error"]}), 400

        # Éxito
        return jsonify({
            "status": "success",
            "data": scan_result
        })

    except Exception as e:
        app.logger.error(f"Error grave: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Error en el servidor",
            "debug": str(e)  # Solo en desarrollo
        }), 500

# API para generación de contraseñas
@app.route('/api/generate_password', methods=['POST'])
def api_generate_password():
    # Validación de entrada
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400
    
    data: Dict[str, Any] = request.get_json()
    length: int = data.get('length', 12)  # Valor por defecto: 12

    try:
        length = int(length)
        if length < 8 or length > 64:
            return jsonify({"error": "La longitud debe estar entre 8 y 64 caracteres"}), 400
            
        # Generación de contraseña
        password: str = generate_strong_password(length)
        
        # Manejo de errores de la función
        if isinstance(password, str) and password.startswith("Error:"):
            return jsonify({"error": password[7:]}), 400
            
        return jsonify({
            "status": "success",
            "length": length,
            "password": password
        })
        
    except ValueError:
        return jsonify({"error": "La longitud debe ser un número válido"}), 400
    except Exception as e:
        app.logger.error(f"Error en generación de contraseña: {str(e)}")
        return jsonify({
            "error": "Error interno del servidor al generar contraseña",
            "details": str(e)
        }), 500

# Manejador de errores 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

# Manejador de errores 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ocurrió un error inesperado"
    }), 500

# Health check para Render
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Inicio de la aplicación
if __name__ == '__main__':
    port: int = int(os.environ.get("PORT", 5000))
    debug: bool = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )