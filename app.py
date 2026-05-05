# app.py — Servidor Flask del chatbot de Paulini Espichan Abogados
# Ejecutar con:  python app.py

import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones desde la web del cliente (dominio externo)


# ─── BASE DE CONOCIMIENTO ────────────────────────────────────────────────────
# Aquí está toda la información del estudio. Modifica aquí para actualizar
# las respuestas del bot sin tocar nada más.

SERVICIOS = {
    "laborales": {
        "titulo": "Litigios Laborales",
        "respuesta": (
            "En **litigios laborales** te ayudamos con:\n\n"
            "• Despido arbitrario (reposición o indemnización)\n"
            "• Pago de CTS, vacaciones y gratificaciones\n"
            "• Horas extras no pagadas\n"
            "• Hostilidad laboral\n"
            "• Accidentes de trabajo y enfermedades profesionales\n\n"
            "La primera consulta es **gratuita**. ¿Quieres hablar con un abogado?"
        ),
    },
    "civiles": {
        "titulo": "Litigios Civiles",
        "respuesta": (
            "En **litigios civiles** te asesoramos en:\n\n"
            "• Incumplimiento de contratos\n"
            "• Desalojo de inmuebles\n"
            "• Daños y perjuicios\n"
            "• Nulidad de actos jurídicos\n"
            "• Cobranza judicial de deudas\n\n"
            "¿Tienes un caso específico? Un abogado puede orientarte sin costo."
        ),
    },
    "empresas": {
        "titulo": "Constitución de Empresas",
        "respuesta": (
            "Constituimos tu empresa (SAC o EIRL) con **todo incluido por S/ 450**:\n\n"
            "✓ Minuta de constitución\n"
            "✓ Escritura pública ante notaría\n"
            "✓ Inscripción en SUNARP\n"
            "✓ RUC en SUNAT\n\n"
            "⚠️ Si el capital social supera S/ 5,350 se hace cotización personalizada.\n\n"
            "¿Quieres empezar el trámite?"
        ),
    },
    "notariales": {
        "titulo": "Actos Notariales",
        "respuesta": (
            "Te apoyamos con todo tipo de **actos notariales**:\n\n"
            "• Poderes notariales (generales y especiales)\n"
            "• Redacción y firma de contratos\n"
            "• Declaraciones juradas\n"
            "• Legalizaciones de firmas y documentos\n\n"
            "¿Qué tipo de documento necesitas? Cuéntanos por WhatsApp."
        ),
    },
    "registral": {
        "titulo": "Soporte Registral",
        "respuesta": (
            "Gestionamos tus trámites ante **Registros Públicos (SUNARP)**:\n\n"
            "• Inscripción de bienes muebles e inmuebles\n"
            "• Levantamiento de hipotecas y embargos\n"
            "• Transferencias de propiedad\n"
            "• Inscripción de personas jurídicas\n\n"
            "¿Tienes algún trámite pendiente? Te ayudamos."
        ),
    },
    "contabilidad": {
        "titulo": "Contabilidad y Tributación",
        "respuesta": (
            "Nuestro equipo contable te ayuda con:\n\n"
            "• Declaraciones mensuales y anuales en SUNAT\n"
            "• Libros contables electrónicos\n"
            "• Planillas de remuneraciones\n"
            "• Asesoría tributaria (NRUS, RER, RMT, Régimen General)\n\n"
            "¿Quieres más información o una cotización?"
        ),
    },
}

# Palabras clave para detectar el tema cuando el usuario escribe libremente
PALABRAS_CLAVE = {
    "laborales": [
        "laboral", "trabajo", "despido", "sueldo", "jefe", "empleado",
        "trabajador", "cts", "vacaciones", "gratificación", "horas extras",
        "accidente laboral", "hostilidad", "beneficios sociales",
    ],
    "civiles": [
        "civil", "contrato", "desalojo", "daños", "perjuicios", "nulidad",
        "deuda", "deudor", "alquiler", "inquilino", "propietario", "arrendamiento",
    ],
    "empresas": [
        "empresa", "constitución", "constituir", "sac", "eirl", "negocio",
        "ruc", "sunarp", "sociedad", "startup", "emprendimiento", "450",
    ],
    "notariales": [
        "notarial", "notario", "poder notarial", "declaración jurada",
        "legalización", "escritura",
    ],
    "registral": [
        "registral", "registros públicos", "sunarp", "hipoteca", "propiedad",
        "transferencia", "embargo", "inscripción",
    ],
    "contabilidad": [
        "contabilidad", "contable", "sunat", "declaración", "tributario",
        "impuesto", "planilla", "libros contables", "régimen tributario",
    ],
}


# ─── LÓGICA DEL CHATBOT ──────────────────────────────────────────────────────

def detectar_servicio(texto):
    """
    Busca palabras clave en el mensaje del usuario para identificar
    de qué servicio está hablando.
    Devuelve la clave del servicio o None si no encuentra ninguna.
    """
    texto = texto.lower()
    for servicio, palabras in PALABRAS_CLAVE.items():
        if any(palabra in texto for palabra in palabras):
            return servicio
    return None


def botones_menu():
    """Devuelve la lista de botones del menú principal."""
    return {
        "botones": list(SERVICIOS.keys()),
        "etiquetas": {k: v["titulo"] for k, v in SERVICIOS.items()},
    }


def respuesta_servicio(clave):
    """Construye la respuesta para un servicio específico."""
    servicio = SERVICIOS[clave]
    return {
        "respuesta": f"📋 **{servicio['titulo']}**\n\n{servicio['respuesta']}",
        "botones": ["ir_whatsapp", "ver_menu"],
        "etiquetas": {
            "ir_whatsapp": "💬 Hablar con un abogado",
            "ver_menu": "← Ver otros servicios",
        },
        "whatsapp": False,
        "estado": f"en_{clave}",
    }


def procesar_mensaje(mensaje, estado):
    """
    Función principal del chatbot.

    Recibe:
        mensaje (str): lo que escribió o seleccionó el usuario
        estado  (str): en qué punto de la conversación estamos

    Devuelve:
        dict con: respuesta, botones, etiquetas, whatsapp (bool), estado
    """
    msg = mensaje.lower().strip()

    # ── 1. SALUDO / INICIO ───────────────────────────────────────────────────
    saludos = ["hola", "hi", "buenas", "buenos días", "buenas tardes",
               "buenas noches", "inicio", "empezar", "comenzar"]

    if estado == "inicio" or msg in saludos:
        menu = botones_menu()
        return {
            "respuesta": (
                "¡Hola! 👋 Bienvenido a **Paulini Espichan Abogados**.\n\n"
                "Estoy aquí para orientarte sobre nuestros servicios legales en Lima. "
                "¿En qué área necesitas ayuda?"
            ),
            "botones": menu["botones"],
            "etiquetas": menu["etiquetas"],
            "whatsapp": False,
            "estado": "menu",
        }

    # ── 2. EL USUARIO SELECCIONÓ UN SERVICIO DEL MENÚ ───────────────────────
    if msg in SERVICIOS:
        return respuesta_servicio(msg)

    # ── 3. BOTÓN "VER MENÚ" ──────────────────────────────────────────────────
    if msg in ["ver_menu", "menu", "menú", "volver", "atrás", "regresar"]:
        menu = botones_menu()
        return {
            "respuesta": "Claro, ¿en cuál de estas áreas puedo orientarte?",
            "botones": menu["botones"],
            "etiquetas": menu["etiquetas"],
            "whatsapp": False,
            "estado": "menu",
        }

    # ── 4. BOTÓN "IR A WHATSAPP" ─────────────────────────────────────────────
    if msg in ["ir_whatsapp", "sí", "si", "quiero", "hablar", "contactar", "conectar"]:
        return {
            "respuesta": (
                "Perfecto 😊 Te conecto con uno de nuestros abogados ahora mismo.\n\n"
                "Recuerda: la **primera consulta es gratuita**. "
                "Haz clic en el botón para abrir WhatsApp."
            ),
            "botones": ["abrir_whatsapp"],
            "etiquetas": {"abrir_whatsapp": "📲 Abrir WhatsApp"},
            "whatsapp": True,
            "estado": "derivado_whatsapp",
        }

    # ── 5. TEXTO LIBRE — detectar por palabras clave ─────────────────────────
    servicio_detectado = detectar_servicio(mensaje)
    if servicio_detectado:
        return respuesta_servicio(servicio_detectado)

    # ── 6. FALLBACK — no entendió la pregunta ────────────────────────────────
    return {
        "respuesta": (
            "Eso escapa de lo que puedo responder aquí, pero uno de nuestros abogados "
            "puede orientarte sin costo. ¿Te conecto por WhatsApp?"
        ),
        "botones": ["ir_whatsapp", "ver_menu"],
        "etiquetas": {
            "ir_whatsapp": "💬 Sí, conectarme",
            "ver_menu": "← Ver servicios",
        },
        "whatsapp": False,
        "estado": estado,
    }


# ─── RUTAS ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Sirve la página de demostración del chatbot."""
    return render_template("demo.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Endpoint principal del chatbot.

    Espera JSON:  { "mensaje": "texto del usuario", "estado": "estado_actual" }
    Devuelve JSON con la respuesta, botones y nuevo estado.
    """
    datos = request.get_json()

    # Validar que llegaron los datos correctos
    if not datos or "mensaje" not in datos:
        return jsonify({"error": "Se requiere el campo 'mensaje'"}), 400

    mensaje = datos.get("mensaje", "").strip()
    estado = datos.get("estado", "inicio")

    # Protección básica: limitar longitud del mensaje
    if len(mensaje) > 500:
        mensaje = mensaje[:500]

    resultado = procesar_mensaje(mensaje, estado)
    return jsonify(resultado)


@app.route("/health")
def health():
    """Ruta de verificación — sirve para comprobar que el servidor está activo."""
    return jsonify({"estado": "ok", "servicio": "Paulini Chatbot"})


# ─── INICIO ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n✅ Chatbot de Paulini Espichan Abogados iniciado")
    print("   Abre tu navegador en:  http://localhost:5000\n")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
