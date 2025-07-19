from flask import Flask, render_template, request, jsonify

# Importación de funciones de ciberseguridad desde la carpeta de components
# Llamado de funciones de componentes
from components.scan_website_ports import scan_website_ports
from components.generate_strong_password import generate_strong_password

app = Flask(__name__, static_folder='static', template_folder='templates')

# Ruta principal de HTML
@app.route('/')
def index():
    return render_template('index.html')

# Ruta API para el análisis de puertos web
@app.route('/api/scan_ports', methods=['POST'])
def api_scan_ports():
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({"error": "No se proporcionó el objetivo."}), 400

    # Llama a la función de escaneo
    result = scan_website_ports(target)

    # Manejo de errores devueltos por la función de escaneo
    if isinstance(result, str) and result.startswith("Error:"):
        return jsonify({"error": result}), 400

    return jsonify({"result": result})

# Ruta API para el generador de contraseñas
@app.route('/api/generate_password', methods=['POST'])
def api_generate_password():
    data = request.get_json()
    length = data.get('length')

    if length is None:
        return jsonify({"error": "No se proporcionó la longitud."}), 400

    # Llamado a la función de generación de contraseña
    password = generate_strong_password(length)

    # Manejo de errores devueltos por la función
    if isinstance(password, str) and password.startswith("Error:"):
        return jsonify({"error": password}), 400

    return jsonify({"password": password})

if __name__ == '__main__':

    app.run(debug=True, port=5000)