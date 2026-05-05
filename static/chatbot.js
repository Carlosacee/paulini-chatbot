// chatbot.js — Widget del chatbot de Paulini Espichan Abogados
// Incluir en cualquier página HTML con:
//   <script src="http://localhost:5000/static/chatbot.js"></script>

// ─── Configuración ───────────────────────────────────────────────────────────
// Cambia esta URL cuando subas el servidor a producción
var CHAT_API_URL = "https://paulini-chatbot-production.up.railway.app/chat";
var WA_URL       = "https://wa.me/51962354342";

// Estado actual de la conversación (se envía en cada petición al servidor)
var estadoActual = "inicio";


// ─── Crear el HTML del widget ────────────────────────────────────────────────
// Esta función construye todo el HTML del widget e inyecta en el <body>
function crearWidget() {
  var div = document.createElement("div");
  div.id = "paulini-chatbot-raiz";
  div.innerHTML = [
    // Botón flotante
    '<div id="paulini-chat-btn" onclick="toggleChat()" title="Chatbot Paulini Abogados">',
      '<div id="paulini-chat-badge">1</div>',
      '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>',
    '</div>',

    // Ventana del chat
    '<div id="paulini-chat-window">',

      // Header
      '<div id="chat-header">',
        '<div class="chat-header-info">',
          '<div class="chat-avatar">⚖️</div>',
          '<div>',
            '<div class="chat-nombre">Paulini Espichan Abogados</div>',
            '<div class="chat-online">',
              '<span class="chat-punto-verde"></span> En línea · Lima, Perú',
            '</div>',
          '</div>',
        '</div>',
        '<button id="btn-cerrar" onclick="toggleChat()" title="Cerrar">✕</button>',
      '</div>',

      // Área de mensajes
      '<div id="chat-mensajes"></div>',

      // Input del usuario
      '<div id="chat-input-area">',
        '<input',
          'id="chat-input"',
          'type="text"',
          'placeholder="Escribe tu consulta..."',
          'onkeydown="manejarTecla(event)"',
          'maxlength="300"',
        '/>',
        '<button id="btn-enviar" onclick="enviarMensaje()" title="Enviar">',
          '<svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>',
        '</button>',
      '</div>',

      // Pie del chat
      '<div id="chat-footer">Paulini Espichan Abogados · Lima, Perú</div>',

    '</div>',
  ].join("");

  document.body.appendChild(div);
}


// ─── Abrir / cerrar el chat ───────────────────────────────────────────────────
function toggleChat() {
  var ventana = document.getElementById("paulini-chat-window");
  var badge   = document.getElementById("paulini-chat-badge");
  var estaAbierto = ventana.classList.contains("abierto");

  if (estaAbierto) {
    // Cerrar
    ventana.classList.remove("abierto");
  } else {
    // Abrir
    ventana.classList.add("abierto");
    if (badge) badge.style.display = "none";

    // Si es la primera vez que se abre, iniciar la conversación
    var area = document.getElementById("chat-mensajes");
    if (area && area.children.length === 0) {
      enviarAlServidor("hola", "inicio");
    }

    // Enfocar el campo de texto
    setTimeout(function() {
      var input = document.getElementById("chat-input");
      if (input) input.focus();
    }, 280);
  }
}


// ─── Enviar cuando el usuario presiona Enter ──────────────────────────────────
function manejarTecla(evento) {
  if (evento.key === "Enter" && !evento.shiftKey) {
    evento.preventDefault();
    enviarMensaje();
  }
}


// ─── Leer lo que escribió el usuario y enviarlo ───────────────────────────────
function enviarMensaje() {
  var input = document.getElementById("chat-input");
  var texto = input.value.trim();
  if (!texto) return;

  // Mostrar el mensaje del usuario en pantalla
  agregarBurbuja(texto, "usuario");
  input.value = "";

  // Enviarlo al servidor Flask
  enviarAlServidor(texto, estadoActual);
}


// ─── Agregar una burbuja de mensaje al área de chat ───────────────────────────
function agregarBurbuja(texto, tipo) {
  var area    = document.getElementById("chat-mensajes");
  var burbuja = document.createElement("div");
  burbuja.className = "burbuja burbuja-" + tipo;

  // Convertir **texto** a negrita y \n a salto de línea
  burbuja.innerHTML = formatearTexto(texto);

  area.appendChild(burbuja);
  scrollAlFondo();
  return burbuja;
}


// ─── Mostrar los puntos de "escribiendo..." ───────────────────────────────────
function mostrarTyping() {
  var area   = document.getElementById("chat-mensajes");
  var typing = document.createElement("div");
  typing.id        = "chat-typing";
  typing.className = "burbuja burbuja-bot typing-dots";
  typing.innerHTML = "<span></span><span></span><span></span>";
  area.appendChild(typing);
  scrollAlFondo();
}

function ocultarTyping() {
  var typing = document.getElementById("chat-typing");
  if (typing) typing.parentNode.removeChild(typing);
}


// ─── Agregar botones de opciones rápidas ─────────────────────────────────────
function agregarBotones(botones, etiquetas) {
  var area = document.getElementById("chat-mensajes");
  var wrap = document.createElement("div");
  wrap.className = "wrap-botones";

  botones.forEach(function(valor) {
    var etiqueta = (etiquetas && etiquetas[valor]) ? etiquetas[valor] : valor;
    var btn = document.createElement("button");
    btn.className = "btn-opcion";
    btn.textContent = etiqueta;

    // Estilo especial para botones de WhatsApp
    if (valor === "ir_whatsapp" || valor === "abrir_whatsapp") {
      btn.classList.add("btn-whatsapp");
    }

    btn.onclick = function() { manejarBoton(valor, etiqueta, wrap); };
    wrap.appendChild(btn);
  });

  area.appendChild(wrap);
  scrollAlFondo();
}


// ─── Manejar clic en un botón de opción ──────────────────────────────────────
function manejarBoton(valor, etiqueta, wrap) {
  // Si es WhatsApp, abrir en nueva pestaña directamente
  if (valor === "ir_whatsapp" || valor === "abrir_whatsapp") {
    window.open(WA_URL, "_blank");
    return;
  }

  // Deshabilitar todos los botones del grupo (evita doble clic)
  var botones = wrap.querySelectorAll(".btn-opcion");
  for (var i = 0; i < botones.length; i++) {
    botones[i].disabled = true;
  }

  // Mostrar la opción seleccionada como mensaje del usuario
  agregarBurbuja(etiqueta, "usuario");

  // Enviar el valor (clave interna) al servidor
  enviarAlServidor(valor, estadoActual);
}


// ─── Comunicación con el servidor Flask ──────────────────────────────────────
function enviarAlServidor(mensaje, estado) {
  mostrarTyping();

  // Preparar los datos a enviar
  var datos = JSON.stringify({ mensaje: mensaje, estado: estado });

  // Usar XMLHttpRequest (compatible con todos los navegadores, sin dependencias)
  var xhr = new XMLHttpRequest();
  xhr.open("POST", CHAT_API_URL, true);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onload = function() {
    // Pequeña pausa para que el indicador de typing se vea natural
    setTimeout(function() {
      ocultarTyping();

      if (xhr.status === 200) {
        var respuesta = JSON.parse(xhr.responseText);

        // Actualizar el estado de la conversación
        if (respuesta.estado) {
          estadoActual = respuesta.estado;
        }

        // Mostrar la respuesta del bot
        agregarBurbuja(respuesta.respuesta, "bot");

        // Mostrar los botones si los hay
        if (respuesta.botones && respuesta.botones.length > 0) {
          setTimeout(function() {
            agregarBotones(respuesta.botones, respuesta.etiquetas);
          }, 150);
        }

      } else {
        // Error del servidor
        agregarBurbuja(
          "Hubo un error al conectarme. Por favor escríbenos directamente por WhatsApp 😊",
          "bot"
        );
        agregarBotones(
          ["abrir_whatsapp"],
          { "abrir_whatsapp": "📲 Abrir WhatsApp" }
        );
      }
    }, 550); // 550ms de espera para que se vea el "typing"
  };

  xhr.onerror = function() {
    // Error de red (servidor apagado, sin conexión, etc.)
    setTimeout(function() {
      ocultarTyping();
      agregarBurbuja(
        "No pude conectarme al servidor. Puedes escribirnos directo por WhatsApp.",
        "bot"
      );
      agregarBotones(
        ["abrir_whatsapp"],
        { "abrir_whatsapp": "📲 Abrir WhatsApp" }
      );
    }, 500);
  };

  xhr.send(datos);
}


// ─── Utilidades ──────────────────────────────────────────────────────────────

// Convierte **texto** → <strong>texto</strong> y \n → <br>
function formatearTexto(texto) {
  return texto
    .replace(/</g, "&lt;")           // Escapar HTML para seguridad
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

// Scroll automático al último mensaje
function scrollAlFondo() {
  var area = document.getElementById("chat-mensajes");
  if (area) {
    setTimeout(function() {
      area.scrollTop = area.scrollHeight;
    }, 40);
  }
}


// ─── Inicialización ───────────────────────────────────────────────────────────
// Esperar a que el DOM esté listo antes de crear el widget
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", crearWidget);
} else {
  // El DOM ya está listo (script cargado al final del body)
  crearWidget();
}
