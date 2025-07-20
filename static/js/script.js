// Efecto de escritura para los placeholders
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

// Inicialización cuando el DOM está listo
document.addEventListener("DOMContentLoaded", function () {
  // Efecto de escritura para los placeholders
  const outputPlaceholders = document.querySelectorAll(
    ".output-placeholder span"
  );
  outputPlaceholders.forEach((placeholder) => {
    typeWriter(placeholder, placeholder.textContent);
  });

  // Efecto hover para las tarjetas
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
});

// Función mejorada para el Análisis de Puertos
async function runPortScan() {
  const targetInput = document.getElementById("port-scan-input");
  const outputArea = document.getElementById("port-scan-output");
  const target = targetInput.value.trim();

  if (!target) {
    showError(
      outputArea,
      "Por favor, ingresa una dirección IP o dominio válido."
    );
    return;
  }

  showLoading(outputArea, "Iniciando escaneo de puertos...");

  try {
    const response = await fetch("/api/scan_ports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Error en el servidor");
    }

    // Formateo mejorado de los resultados
    let resultText = `
      Target: ${data.data.target || "No disponible"}
      IP: ${data.data.ip || "No resuelta"}
      Tiempo: ${data.data.scan_time || "?"}
      Puertos escaneados: ${data.data.scanned_ports || "?"}
      
      Puertos abiertos:
    `;

    if (data.data.open_ports && data.data.open_ports.length > 0) {
      data.data.open_ports.forEach((port) => {
        resultText += `
        • Puerto ${port.port}: ${port.service || "servicio desconocido"} (${
          port.response_time
        })`;
      });
    } else {
      resultText += "      Ningún puerto abierto encontrado";
    }

    showResult(outputArea, resultText);
  } catch (error) {
    showError(outputArea, error.message);
  }
}

// Función mejorada para el Generador de Contraseñas
async function generatePassword() {
  const lengthInput = document.getElementById("password-length");
  const outputArea = document.getElementById("password-generator-output");
  const length = parseInt(lengthInput.value);

  // Validación de entrada
  if (isNaN(length) || length < 8 || length > 64) {
    showError(outputArea, "La longitud debe ser un número entre 8 y 64.");
    return;
  }

  // Mostrar estado de carga
  showLoading(outputArea, "Generando contraseña segura...");

  //Conexion de JS a Python para Generador de Contraseña (App.py)
  try {
    const response = await fetch("/api/generate_password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ length }),
    });

    const data = await response.json();

    if (response.ok) {
      showPasswordResult(outputArea, data.password);
    } else {
      showError(outputArea, data.error || "Error al generar la contraseña.");
    }
  } catch (error) {
    showError(outputArea, `Error de conexión: ${error.message}`);
  }
}

// Función para reiniciar el sistema
function resetSystem() {
  // Limpiar entradas
  document.getElementById("port-scan-input").value = "";
  document.getElementById("password-length").value = "16";

  // Restablecer áreas de salida
  const outputs = document.querySelectorAll(".cyber-output");
  outputs.forEach((output) => {
    output.innerHTML = `
      <div class="output-placeholder">
        <i class="bi bi-terminal"></i>
        <span>${
          output.id === "port-scan-output"
            ? "Resultados del escaneo aparecerán aquí..."
            : "Tu contraseña segura aparecerá aquí..."
        }</span>
      </div>
    `;

    // Volver a aplicar el efecto de escritura
    const placeholder = output.querySelector(".output-placeholder span");
    typeWriter(placeholder, placeholder.textContent);
  });

  // Mostrar notificación de éxito
  // Codigo a Mejorar por errores de aparencia
  //showNotification("Sistema reiniciado correctamente", "success");
}

// Funciones auxiliares para mostrar resultados
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
  element.innerHTML = `<pre class="m-0">${content}</pre>`;
  element.scrollTop = element.scrollHeight;
}

function showPasswordResult(element, password) {
  element.innerHTML = `
    <div class="password-result">
      <div class="password-strength mb-3">
        <div class="strength-meter">
          <div class="strength-bar" style="width: ${calculateStrength(
            password
          )}%"></div>
        </div>
        <div class="strength-label">Seguridad: ${getStrengthLabel(
          password
        )}</div>
      </div>
      <div class="generated-password">
        <code>${password}</code>
        <button class="btn btn-copy" onclick="copyToClipboard('${password}')">
          <i class="bi bi-clipboard"></i>
        </button>
      </div>
      <div class="password-info mt-2">
        <small>Longitud: ${
          password.length
        } caracteres | Entropía: ${calculateEntropy(password).toFixed(
    2
  )} bits</small>
      </div>
    </div>
  `;
}

function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <i class="bi ${
      type === "success"
        ? "bi-check-circle-fill"
        : type === "error"
        ? "bi-exclamation-circle-fill"
        : "bi-info-circle-fill"
    } me-2"></i>
    <span>${message}</span>
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.add("show");
    setTimeout(() => {
      notification.classList.remove("show");
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }, 100);
}

// Funciones auxiliares para contraseñas
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

function getStrengthLabel(password) {
  const strength = calculateStrength(password);
  if (strength < 40) return "Débil";
  if (strength < 70) return "Moderada";
  if (strength < 90) return "Fuerte";
  return "Muy Fuerte";
}

function calculateEntropy(password) {
  const poolSize =
    (/[a-z]/.test(password) ? 26 : 0) +
    (/[A-Z]/.test(password) ? 26 : 0) +
    (/\d/.test(password) ? 10 : 0) +
    (/[^a-zA-Z0-9]/.test(password) ? 32 : 0);

  return password.length * Math.log2(poolSize || 1);
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

// Formateador de resultados de escaneo de puertos
/*function formatPortScanResults(results) {
  if (!results) return "No se encontraron resultados.";

  // Si ya está formateado (como texto preformateado)
  if (typeof results === "string") return results;

  // Si es un objeto JSON, formatearlo
  if (typeof results === "object") {
    let formatted = `Resultados del escaneo para ${
      results.target || "objetivo desconocido"
    }:\n\n`;
    formatted += `Estado: ${results.status || "desconocido"}\n`;
    formatted += `Tiempo: ${results.time || "?"} ms\n\n`;

    if (results.openPorts && results.openPorts.length > 0) {
      formatted += "PUERTOS ABIERTOS:\n";
      formatted += "-----------------\n";
      results.openPorts.forEach((port) => {
        formatted += `• Puerto ${port.port}: ${
          port.service || "servicio desconocido"
        }\n`;
      });
    } else {
      formatted += "No se encontraron puertos abiertos.\n";
    }

    return formatted;
  }

  return results.toString();
}*/
function formatPortScanResults(data) {
  if (!data) return "No se encontraron resultados.";

  let formatted = `=== RESULTADOS DEL ESCANEO ===\n\n`;
  formatted += `Objetivo: ${data.target || "Desconocido"}\n`;
  formatted += `Dirección IP: ${data.ip_address || "No resuelta"}\n`;
  formatted += `Puertos escaneados: ${data.ports_scanned || "?"}\n`;
  formatted += `Tiempo de escaneo: ${data.scan_time || "?"} segundos\n\n`;

  if (data.open_ports && data.open_ports.length > 0) {
    formatted += "PUERTOS ABIERTOS:\n";
    formatted += "-----------------\n";
    data.open_ports.forEach((port) => {
      formatted += `• Puerto ${port}\n`;
    });
  } else {
    formatted += "No se encontraron puertos abiertos.\n";
  }

  return formatted;
}
