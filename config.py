"""
Configuración del Asistente por Voz para Antigravity CLI (agy)
"""

# ==========================================
# 1. PALABRA DE ACTIVACIÓN (WAKE WORD)
# ==========================================
WAKE_WORDS = ["alexa"]
WAKE_WORD_THRESHOLD = 0.5

# ==========================================
# 2. TECLA DE ATAJO GLOBAL (PUSH-TO-TALK / TOGGLE)
# ==========================================
HOTKEY_PUSH_TO_TALK = "f8"

# ==========================================
# 3. CONFIGURACIÓN DE AUDIO Y MICRÓFONO
# ==========================================
SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
INPUT_DEVICE_INDEX = None

SILENCE_THRESHOLD = 0.001
SILENCE_DURATION = 2.2
MIN_RECORD_SECONDS = 1.5
MAX_RECORD_SECONDS = 300.0  # Límite máximo de seguridad (5 min); el fin de la grabación lo determina el silencio al terminar de hablar


# ==========================================
# 4. CONFIGURACIÓN DE WHISPER (STT)
# ==========================================
WHISPER_MODEL_SIZE = "small"
WHISPER_LANGUAGE = "es"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

WHISPER_PROMPT_BIAS = (
    "Hola mundo, crear función, git status, git commit, refactorizar código, "
    "corregir bug, crear componente, endpoint de API, ejecutar servidor, "
    "instalar paquete, python, javascript, typescript, docker, terminal, archivo, "
    "Midudev, YouTube, Netflix, Google, Spotify, Mercado Libre."
)

# ==========================================
# 5. INTEGRACIÓN CON ANTIGRAVITY CLI (AGY)
# ==========================================
SESSION_MEMORY_MODE = "per_session"
AGY_PROJECT_ID = "asistente-voz"
AGY_PRINT_TIMEOUT = "20m"
CONTINUE_PREVIOUS_CONVERSATION = True
AGY_COMMAND = "agy"
DEFAULT_PROJECT_DIR = None
AGY_MODEL = None
AGY_REASONING_EFFORT = None
DYNAMIC_REASONING_EFFORT = True

# ==========================================
# 6. RESPUESTA POR VOZ (TEXT-TO-SPEECH - TTS)
# ==========================================
TTS_ENABLED = True
TTS_VOICE = "es-ES-AlvaroNeural"
TTS_RATE = "+25%"

# ==========================================
# 7. FEEDBACK AUDIBLE (BEEPS)
# ==========================================
SOUND_FEEDBACK_ENABLED = True

# ==========================================
# 8. INSPECCIÓN VISUAL Y LECTURA DE PANTALLA
# ==========================================
SCREEN_OCR_MIN_CHARS = 30

