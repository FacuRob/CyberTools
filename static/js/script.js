// Efecto de escritura para placeholders
function typeWriter(element, text, speed = 50) {
  let i = 0;
  element.innerHTML = "";
  const cursor = document.createElement("span");
  cursor.className = "blinking-cursor";
  cursor.innerHTML = "|";
  element.appendChild(cursor);

  function typing() {
    if (i < text.length) {
      element.insertBefore(document.createTextNode(text.charAt(i)), cursor);
      i++;
      setTimeout(typing, speed);
    } else {
      cursor.style.display = "none";
    }
  }

  setTimeout(typing, 500);
}

// Inicialización DOM
document.addEventListener("DOMContentLoaded", function () {
  // Actualizar año automáticamente
  const currentYearElement = document.getElementById("current-year");
  if (currentYearElement) {
    currentYearElement.textContent = new Date().getFullYear();
  }

  const outputPlaceholders = document.querySelectorAll(".output-placeholder span");
  outputPlaceholders.forEach((placeholder) => {
    typeWriter(placeholder, placeholder.textContent);
  });

  // Efectos hover para tarjetas
  const cards = document.querySelectorAll(".cyber-card");
  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-5px)";
      this.style.boxShadow = "0 15px 30px rgba(0, 240, 255, 0.1)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "";
      this.style.boxShadow = "0 10px 20px rgba(0, 0, 0, 0.3)";
    });
  });

  // File upload zone
  setupFileUpload();
});

// ======== ANÁLISIS DE PUERTOS (MEJORADO) ========
async function runPortScan() {
  const targetInput = document.getElementById("port-scan-input");
  const outputArea = document.getElementById("port-scan-output");
  const target = targetInput.value.trim();

  if (!target) {
    showError(outputArea, "Por favor, ingresa una dirección IP o dominio válido.");
    return;
  }

  showLoading(outputArea, "Iniciando escaneo optimizado...");

  try {
    const response = await fetch("/api/scan_ports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || result.error || "Error en el servidor");
    }

    const data = result.data;

    // Formateo mejorado con métricas de rendimiento
    let resultText = `╔══════════════════════════════════════╗
║   RESULTADOS DEL ESCANEO OPTIMIZADO   ║
╚══════════════════════════════════════╝

🎯 Target: ${data.target}
🌐 IP: ${data.ip}
⏱️  Tiempo total: ${data.scan_time}
📊 Puertos escaneados: ${data.scanned_ports}
✅ Puertos abiertos: ${data.open_count || 0}
⚡ Tiempo promedio/puerto: ${data.avg_time_per_port || '?'}

`;

    if (data.open_ports && data.open_ports.length > 0) {
      resultText += `╔════════════════════════════════════╗
║        PUERTOS ABIERTOS             ║
╚════════════════════════════════════╝

`;
      data.open_ports.forEach((port) => {
        const service = port.service || "unknown";
        const time = port.response_time || "?";
        resultText += `🔓 Puerto ${String(port.port).padEnd(6)} │ ${service.padEnd(15)} │ ${time}\n`;
      });
    } else {
      resultText += `╔════════════════════════════════════╗
║    NO HAY PUERTOS ABIERTOS         ║
╚════════════════════════════════════╝

✓ Sistema bien protegido o filtrado`;
    }

    resultText += `

📅 ${data.timestamp}`;

    showResult(outputArea, resultText);
    showNotification(`Escaneo completado: ${data.open_count || 0} puertos abiertos`, "success");

  } catch (error) {
    showError(outputArea, `❌ ${error.message}`);
    showNotification("Error en el escaneo", "error");
  }
}

// ======== GENERADOR DE CONTRASEÑAS (MEJORADO) ========
async function generatePassword() {
  const lengthInput = document.getElementById("password-length");
  const phraseInput = document.getElementById("password-phrase");
  const outputArea = document.getElementById("password-generator-output");

  // Obtener configuración
  const length = parseInt(lengthInput.value);
  const phrase = phraseInput.value.trim();
  const useUppercase = document.getElementById("use-uppercase").checked;
  const useNumbers = document.getElementById("use-numbers").checked;
  const useSymbols = document.getElementById("use-symbols").checked;

  // Validación
  if (isNaN(length) || length < 8 || length > 64) {
    showError(outputArea, "❌ La longitud debe estar entre 8 y 64.");
    return;
  }

  // Verificar que al menos una opción esté seleccionada (además de minúsculas)
  if (!useUppercase && !useNumbers && !useSymbols && !phrase) {
    showNotification("Al menos debe incluir un tipo de carácter adicional", "info");
  }

  showLoading(outputArea, phrase ? "Generando desde frase..." : "Generando contraseña aleatoria...");

  try {
    const response = await fetch("/api/generate_password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        length: length,
        phrase: phrase || null,
        use_uppercase: useUppercase,
        use_numbers: useNumbers,
        use_symbols: useSymbols
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showPasswordResult(outputArea, data);
      showNotification("Contraseña generada exitosamente", "success");
    } else {
      showError(outputArea, `❌ ${data.error || "Error al generar"}`);
    }
  } catch (error) {
    showError(outputArea, `❌ Error de conexión: ${error.message}`);
    showNotification("Error al generar contraseña", "error");
  }
}

// ======== FUNCIONES AUXILIARES ========
function resetSystem() {
  // Limpiar inputs
  document.getElementById("port-scan-input").value = "";
  document.getElementById("password-phrase").value = "";
  document.getElementById("password-length").value = "16";

  // Resetear checkboxes
  document.getElementById("use-uppercase").checked = true;
  document.getElementById("use-numbers").checked = true;
  document.getElementById("use-symbols").checked = true;

  // Limpiar outputs
  const outputs = document.querySelectorAll(".cyber-output");
  outputs.forEach((output) => {
    const isPortScan = output.id === "port-scan-output";
    const isMetadata = output.id === "metadata-output";

    let placeholderText = "Tu contraseña segura aparecerá aquí...";
    if (isPortScan) {
      placeholderText = "Resultados del escaneo aparecerán aquí...";
    } else if (isMetadata) {
      placeholderText = "Resultados del análisis aparecerán aquí...";
    }

    output.innerHTML = `
      <div class="output-placeholder">
        <i class="bi bi-terminal"></i>
        <span>${placeholderText}</span>
      </div>
    `;

    const placeholder = output.querySelector(".output-placeholder span");
    typeWriter(placeholder, placeholder.textContent);
  });

  // Limpiar archivo seleccionado
  removeFile();

  showNotification("Sistema reiniciado correctamente", "success");
}

function showLoading(element, message) {
  element.innerHTML = `
    <div class="d-flex align-items-center text-cyan">
      <div class="spinner-border spinner-border-sm me-2" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
      <span>${message}</span>
    </div>
  `;
}

function showError(element, message) {
  element.innerHTML = `
    <div class="text-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <span>${message}</span>
    </div>
  `;
}

function showResult(element, content) {
  element.innerHTML = `<pre class="m-0" style="height: 100%;">${content}</pre>`;
  element.scrollTop = element.scrollHeight;
}

// Mostrar resultado de contraseña con análisis
function showPasswordResult(element, data) {
  const { password, analysis, generated_from_phrase } = data;

  const strengthColor =
    analysis.strength === "Muy Fuerte" ? "success" :
      analysis.strength === "Fuerte" ? "info" :
        analysis.strength === "Moderada" ? "warning" : "danger";

  element.innerHTML = `
    <div class="password-result">
      ${generated_from_phrase ?
      '<div class="alert alert-info py-2 mb-3"><i class="bi bi-lightbulb"></i> Generada desde tu frase</div>' :
      '<div class="alert alert-secondary py-2 mb-3"><i class="bi bi-shuffle"></i> Generada aleatoriamente</div>'
    }
      
      <div class="password-strength mb-3">
        <div class="strength-meter">
          <div class="strength-bar bg-${strengthColor}" style="width: ${calculateStrengthPercentage(analysis)}%"></div>
        </div>
        <div class="strength-label d-flex justify-content-between mt-2">
          <span>Seguridad: <strong class="text-${strengthColor}">${analysis.strength}</strong></span>
          <span>Entropía: <strong>${analysis.entropy_bits} bits</strong></span>
        </div>
      </div>
      
      <div class="generated-password">
        <code id="generated-pwd">${password}</code>
        <button class="btn btn-copy" onclick="copyToClipboard('${password}')" title="Copiar">
          <i class="bi bi-clipboard"></i>
        </button>
      </div>
      
      <div class="password-info mt-3">
        <div class="row text-center small">
          <div class="col-3">
            <div class="info-badge ${analysis.has_uppercase ? 'active' : ''}">
              <i class="bi bi-type"></i>
              <div>ABC</div>
            </div>
          </div>
          <div class="col-3">
            <div class="info-badge ${analysis.has_numbers ? 'active' : ''}">
              <i class="bi bi-123"></i>
              <div>123</div>
            </div>
          </div>
          <div class="col-3">
            <div class="info-badge ${analysis.has_symbols ? 'active' : ''}">
              <i class="bi bi-asterisk"></i>
              <div>!@#</div>
            </div>
          </div>
          <div class="col-3">
            <div class="info-badge active">
              <i class="bi bi-rulers"></i>
              <div>${analysis.length}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function calculateStrengthPercentage(analysis) {
  const entropy = analysis.entropy_bits;
  if (entropy < 40) return 25;
  if (entropy < 60) return 50;
  if (entropy < 80) return 75;
  return 100;
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;

  const icons = {
    success: "bi-check-circle-fill",
    error: "bi-exclamation-circle-fill",
    info: "bi-info-circle-fill"
  };

  notification.innerHTML = `
    <i class="bi ${icons[type] || icons.info} me-2"></i>
    <span>${message}</span>
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.add("show");
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }, 100);
}

function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      showNotification("Contraseña copiada al portapapeles", "success");
    })
    .catch((err) => {
      showNotification("Error al copiar: " + err, "error");
    });
}

// Funciones legacy para compatibilidad
function calculateStrength(password) {
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSymbols = /[^a-zA-Z0-9]/.test(password);
  const length = password.length;

  let strength = 0;
  if (length >= 8) strength += 20;
  if (length >= 12) strength += 20;
  if (length >= 16) strength += 20;
  if (hasLower && hasUpper) strength += 15;
  if (hasNumbers) strength += 10;
  if (hasSymbols) strength += 15;

  return Math.min(strength, 100);
}

// ======== ANALIZADOR DE METADATOS (NUEVO) ========

let selectedFile = null;

function setupFileUpload() {
  const fileInput = document.getElementById("file-input");
  const uploadZone = document.getElementById("file-upload-zone");

  if (!fileInput || !uploadZone) return;

  // Click en zona de upload
  uploadZone.addEventListener("click", () => {
    fileInput.click();
  });

  // Selección de archivo
  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileSelect(file);
    }
  });

  // Drag and drop
  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
  });

  uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("dragover");
  });

  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");

    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  });
}

function handleFileSelect(file) {
  // Validar tamaño (16MB)
  if (file.size > 16 * 1024 * 1024) {
    showNotification("Archivo muy grande (máx 16MB)", "error");
    return;
  }

  // Validar extensión
  const validExtensions = [
    'pdf', 'docx', 'doc', 'xlsx', 'xls', 'txt', 'log', 'md',
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'
  ];

  const fileName = file.name.toLowerCase();
  const fileExt = fileName.split('.').pop();

  if (!validExtensions.includes(fileExt)) {
    showNotification(`Tipo de archivo no soportado: .${fileExt}`, "error");
    return;
  }

  selectedFile = file;

  // Mostrar archivo seleccionado
  document.querySelector(".upload-placeholder").style.display = "none";
  const fileSelected = document.getElementById("file-selected");
  fileSelected.style.display = "flex";
  document.getElementById("file-name").textContent = file.name;

  showNotification("Archivo cargado correctamente", "success");
}

function removeFile() {
  selectedFile = null;
  const fileInput = document.getElementById("file-input");
  if (fileInput) fileInput.value = "";

  document.querySelector(".upload-placeholder").style.display = "flex";
  const fileSelected = document.getElementById("file-selected");
  if (fileSelected) fileSelected.style.display = "none";
}

async function analyzeMetadata() {
  const outputArea = document.getElementById("metadata-output");

  if (!selectedFile) {
    showError(outputArea, "❌ Por favor, selecciona un archivo primero");
    showNotification("Selecciona un archivo para analizar", "error");
    return;
  }

  showLoading(outputArea, "Analizando metadatos del archivo...");

  try {
    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch("/api/analyze_metadata", {
      method: "POST",
      body: formData
    });

    // Verificar si la respuesta es JSON
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("Respuesta del servidor no es JSON. Verifica que el servidor esté corriendo.");
    }

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || result.message || "Error analizando archivo");
    }

    const data = result.data;

    // Formatear resultados
    let output = `╔══════════════════════════════════════════════╗
║      ANÁLISIS DE METADATOS COMPLETO          ║
╚══════════════════════════════════════════════╝

📄 INFORMACIÓN DEL ARCHIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nombre: ${data.file_info.filename}
Tamaño: ${data.file_info.size}
Tipo: ${data.file_type.toUpperCase()}
MIME: ${data.file_info.mime_type}
Extensión: ${data.file_info.extension}

📅 FECHAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Creado: ${data.file_info.created}
Modificado: ${data.file_info.modified}
Accedido: ${data.file_info.accessed}

`;

    // Metadatos específicos
    if (data.metadata && !data.metadata.error) {
      output += `🔍 METADATOS ESPECÍFICOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;

      const meta = data.metadata;

      // Imágenes
      if (meta.dimensions) {
        output += `Dimensiones: ${meta.dimensions}
Formato: ${meta.format || '?'}
Modo: ${meta.mode || '?'}
`;
      }

      // PDFs
      if (meta.pages !== undefined) {
        output += `Páginas: ${meta.pages}
Encriptado: ${meta.encrypted ? 'Sí' : 'No'}
`;
      }

      // Word/Excel
      if (meta.paragraphs !== undefined) {
        output += `Párrafos: ${meta.paragraphs}
Tablas: ${meta.tables || 0}
Secciones: ${meta.sections || 0}
`;
      }

      if (meta.sheets !== undefined) {
        output += `Hojas: ${meta.sheets}
Nombres: ${meta.sheet_names.join(', ')}
`;
      }

      // Propiedades de documento
      if (meta.document_properties || meta.document_info) {
        const props = meta.document_properties || meta.document_info;
        output += `
📋 PROPIEDADES DEL DOCUMENTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
        for (const [key, value] of Object.entries(props)) {
          if (value && value !== 'Unknown' && value !== 'None' && value !== 'Untitled') {
            output += `${key}: ${value}
`;
          }
        }
      }

      // Datos sensibles
      if (meta.sensitive_data && Object.keys(meta.sensitive_data).length > 0) {
        output += `
⚠️  DATOS POTENCIALMENTE SENSIBLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
        for (const [key, value] of Object.entries(meta.sensitive_data)) {
          output += `${key}: ${value}
`;
        }
      }

      // EXIF
      if (meta.exif && meta.exif !== null) {
        if (typeof meta.exif === 'object' && Object.keys(meta.exif).length > 0) {
          output += `
📷 DATOS EXIF DETECTADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total campos EXIF: ${meta.exif_count || Object.keys(meta.exif).length}
`;
          // Mostrar solo campos importantes
          const importantFields = ['Make', 'Model', 'Software', 'DateTime',
            'DateTimeOriginal', 'GPSInfo', 'GPSLatitude',
            'GPSLongitude', 'Artist', 'Copyright'];
          let shownFields = 0;
          for (const field of importantFields) {
            if (meta.exif[field]) {
              output += `${field}: ${meta.exif[field]}
`;
              shownFields++;
            }
          }
          if (shownFields === 0) {
            // Mostrar primeros 5 campos si no hay campos importantes
            let count = 0;
            for (const [key, value] of Object.entries(meta.exif)) {
              if (count < 5) {
                output += `${key}: ${value}
`;
                count++;
              }
            }
            if (Object.keys(meta.exif).length > 5) {
              output += `... y ${Object.keys(meta.exif).length - 5} campos más
`;
            }
          }
        }
      } else if (meta.exif_note) {
        output += `
📷 DATOS EXIF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${meta.exif_note}
`;
      }

      // Información adicional
      if (meta.additional_info) {
        output += `
ℹ️  INFORMACIÓN ADICIONAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
        for (const [key, value] of Object.entries(meta.additional_info)) {
          output += `${key}: ${value}
`;
        }
      }
    } else if (data.metadata && data.metadata.error) {
      output += `
⚠️  ERROR EN ANÁLISIS ESPECÍFICO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
${data.metadata.error}
`;
    }

    // Advertencias de seguridad
    if (data.warnings && data.warnings.length > 0) {
      output += `
🔒 ANÁLISIS DE SEGURIDAD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
      data.warnings.forEach(warning => {
        output += `${warning}
`;
      });
    }

    output += `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Análisis completado: ${data.timestamp}`;

    showResult(outputArea, output);
    showNotification("Análisis completado exitosamente", "success");

  } catch (error) {
    console.error("Error completo:", error);
    showError(outputArea, `❌ Error: ${error.message}`);
    showNotification("Error en el análisis - Verifica la consola", "error");
  }
}