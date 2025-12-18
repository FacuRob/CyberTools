import os
from flask import Flask, render_template, request, jsonify
from typing import Optional, Dict, Any, List
from werkzeug.utils import secure_filename
from components.scan_website_ports import scan_website_ports
from components.generate_strong_password import generate_strong_password, analyze_password_strength
from components.analyze_metadata import analyze_metadata

app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuración
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {
    'pdf', 'docx', 'doc', 'xlsx', 'xls', 'txt', 'log', 'md',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'
}

# Crear carpeta de uploads si no existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images/logo.ico')
def favicon():
    return app.send_static_file('images/logo.ico')

# API de escaneo de puertos (mejorada)
@app.route('/api/scan_ports', methods=['POST'])
def api_scan_ports():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Se esperaba JSON"}), 400

        data = request.get_json()
        target = data.get('target', '').strip()
        
        if not target:
            return jsonify({"status": "error", "message": "Target requerido"}), 400

        # Puertos personalizados o comunes
        custom_ports = data.get('ports', [80, 443, 22, 21, 8080, 3306, 3389])

        if not isinstance(custom_ports, list):
            return jsonify({"status": "error", "message": "Puertos deben ser una lista"}), 400

        # Validar puertos (entre 1 y 65535)
        valid_ports = [p for p in custom_ports if isinstance(p, int) and 1 <= p <= 65535]
        if not valid_ports:
            return jsonify({"status": "error", "message": "No hay puertos válidos"}), 400

        # Escanear
        scan_result = scan_website_ports(target, valid_ports)
        
        if "error" in scan_result:
            return jsonify({"status": "error", "message": scan_result["error"]}), 400

        return jsonify({
            "status": "success",
            "data": scan_result
        })

    except Exception as e:
        app.logger.error(f"Error en escaneo: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "Error en el servidor",
            "debug": str(e)
        }), 500

# API de generación de contraseñas (MEJORADA)
@app.route('/api/generate_password', methods=['POST'])
def api_generate_password():
    try:
        if not request.is_json:
            return jsonify({"error": "Se esperaba JSON"}), 400
        
        data: Dict[str, Any] = request.get_json()
        
        # Parámetros
        length: int = data.get('length', 16)
        phrase: str = data.get('phrase', '').strip()  # NUEVO
        use_numbers: bool = data.get('use_numbers', True)  # NUEVO
        use_symbols: bool = data.get('use_symbols', True)  # NUEVO
        use_uppercase: bool = data.get('use_uppercase', True)  # NUEVO
        
        # Validación de longitud
        try:
            length = int(length)
            if length < 8 or length > 64:
                return jsonify({"error": "Longitud entre 8 y 64"}), 400
        except ValueError:
            return jsonify({"error": "Longitud debe ser un número"}), 400
        
        # Validación de frase (si existe)
        if phrase:
            words = phrase.split()
            if len(words) < 2:
                return jsonify({"error": "La frase debe tener al menos 2 palabras"}), 400
            if len(phrase) > 200:
                return jsonify({"error": "Frase demasiado larga (máx 200 caracteres)"}), 400
        
        # Validar que al menos un tipo esté seleccionado
        if not (use_numbers or use_symbols or use_uppercase):
            # Al menos minúsculas siempre están activas
            pass
        
        # Generar contraseña
        password: str = generate_strong_password(
            length=length,
            phrase=phrase if phrase else None,
            use_numbers=use_numbers,
            use_symbols=use_symbols,
            use_uppercase=use_uppercase
        )
        
        # Analizar fortaleza
        analysis = analyze_password_strength(password)
        
        return jsonify({
            "status": "success",
            "password": password,
            "length": len(password),
            "analysis": analysis,
            "generated_from_phrase": bool(phrase)
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.error(f"Error generando contraseña: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error interno del servidor",
            "details": str(e)
        }), 500

# API de análisis de metadatos (NUEVO)
@app.route('/api/analyze_metadata', methods=['POST'])
def api_analyze_metadata():
    try:
        # Verificar si hay archivo
        if 'file' not in request.files:
            app.logger.warning("No file in request")
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            app.logger.warning("Empty filename")
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        # Validar extensión
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        if file_ext not in app.config['ALLOWED_EXTENSIONS']:
            app.logger.warning(f"Unsupported extension: {file_ext}")
            return jsonify({
                "error": f"Tipo de archivo no soportado: .{file_ext}",
                "supported": list(app.config['ALLOWED_EXTENSIONS'])
            }), 400
        
        # Guardar archivo de forma segura
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        app.logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        try:
            # Analizar metadatos
            app.logger.info(f"Analyzing metadata for: {filename}")
            result = analyze_metadata(filepath)
            
            # Eliminar archivo después del análisis
            if os.path.exists(filepath):
                os.remove(filepath)
                app.logger.info(f"File deleted: {filepath}")
            
            if "error" in result and result.get("status") != "success":
                app.logger.error(f"Analysis error: {result['error']}")
                return jsonify({"error": result["error"]}), 400
            
            app.logger.info(f"Analysis completed successfully for: {filename}")
            return jsonify({
                "status": "success",
                "data": result
            })
            
        except Exception as e:
            # Limpiar archivo en caso de error
            if os.path.exists(filepath):
                os.remove(filepath)
                app.logger.info(f"File deleted after error: {filepath}")
            raise e
            
    except Exception as e:
        app.logger.error(f"Error en análisis de metadatos: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Error procesando el archivo",
            "details": str(e)
        }), 500

def allowed_file(filename: str) -> bool:
    """Verifica si la extensión del archivo está permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Manejadores de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Error interno del servidor",
        "message": "Ocurrió un error inesperado"
    }), 500

# Health check
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "version": "2.0"}), 200

# Información del sistema (útil para debugging)
@app.route('/api/info')
def api_info():
    return jsonify({
        "app": "CyberTools",
        "version": "2.1",
        "features": {
            "port_scanner": {
                "optimized": True,
                "max_workers": 100,
                "timeout": "1.5s",
                "caching": True
            },
            "password_generator": {
                "phrase_based": True,
                "configurable": True,
                "max_length": 64
            },
            "metadata_analyzer": {
                "enabled": True,
                "supported_formats": list(app.config['ALLOWED_EXTENSIONS']),
                "max_file_size": "16MB"
            }
        }
    })

if __name__ == '__main__':
    port: int = int(os.environ.get("PORT", 5000))
    debug: bool = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )