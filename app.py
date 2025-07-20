import os
from flask import Flask, render_template, request, jsonify
from components.scan_website_ports import scan_website_ports
from components.generate_strong_password import generate_strong_password

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración básica (opcional)
app.config['JSON_SORT_KEYS'] = False  # Para mantener el orden en las respuestas JSON

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
    # Validación de entrada
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400
    
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({"error": "Se requiere el parámetro 'target'"}), 400

    try:
        # Lógica de escaneo
        result = scan_website_ports(target)
        
        # Manejo de errores de la función
        if isinstance(result, str) and result.startswith("Error:"):
            return jsonify({"error": result[7:]}), 400  # Remueve "Error:" del mensaje
            
        return jsonify({
            "status": "success",
            "target": target,
            "open_ports": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

# API para generación de contraseñas
@app.route('/api/generate_password', methods=['POST'])
def api_generate_password():
    # Validación de entrada
    if not request.is_json:
        return jsonify({"error": "El contenido debe ser JSON"}), 400
    
    data = request.get_json()
    length = data.get('length', 12)  # Valor por defecto: 12

    try:
        length = int(length)
        if length < 8 or length > 64:
            return jsonify({"error": "La longitud debe estar entre 8 y 64 caracteres"}), 400
            
        # Generación de contraseña
        password = generate_strong_password(length)
        
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
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

# Manejador de errores 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

# Inicio de la aplicación
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        threaded=True  # Permite manejar múltiples solicitudes
    )