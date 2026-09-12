"""
Módulo de Transcripción de Audio a Texto usando Faster-Whisper con Limpieza Inteligente de Titubeos.
"""
import re
import numpy as np
from faster_whisper import WhisperModel
import config

# Frases explícitas de cancelación
CANCEL_PHRASES = {
    "no nada", "cancela", "cancelar", "olvidalo", "olvídalo",
    "espera", "nada", "parar", "deja", "déjalo"
}

# Patrones de muletillas o titubeos iniciales
INITIAL_FILLERS = r'^(eh+|em+|este+|mmm+|o sea|a ver|bueno|o sea que|digamos)\b[\s,]*'

class WhisperTranscriber:
    def __init__(self):
        print(f"📦 Inicializando Faster-Whisper ({config.WHISPER_MODEL_SIZE}) en {config.WHISPER_DEVICE}...")
        self.model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE
        )
        print(f"✅ Modelo Faster-Whisper ({config.WHISPER_MODEL_SIZE}) cargado correctamente.")

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribe un array de audio float32 (16kHz).
        Retorna el texto transcrito.
        """
        if audio_data is None or len(audio_data) == 0:
            return ""

        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        segments, info = self.model.transcribe(
            audio_data,
            language=config.WHISPER_LANGUAGE,
            initial_prompt=config.WHISPER_PROMPT_BIAS,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=600)
        )

        text_parts = [segment.text.strip() for segment in segments]
        raw_transcription = " ".join(text_parts).strip()
        return raw_transcription

    def clean_and_validate(self, text: str) -> tuple[str, bool, str]:
        """
        Limpia titubeos, elimina muletillas y valida si la instrucción es ejecutable.
        Retorna (texto_limpio, es_valido, motivo_si_no_es_valido).
        """
        if not text or not text.strip():
            return "", False, "Audio sin palabras detectadas"

        cleaned = text.strip()

        # 1. Corrección fonética común: "hola mundos" -> "hola mundo"
        cleaned = re.sub(r'\bhola\s+mundos\b', 'hola mundo', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bmi\s+dudev\b', 'midudev', cleaned, flags=re.IGNORECASE)

        # 2. Eliminar repeticiones por tartamudeo ("crea crea un", "el el archivo")
        cleaned = re.sub(r'\b(\w+)\s+\1\b', r'\1', cleaned, flags=re.IGNORECASE)

        # 3. Eliminar muletillas al inicio de la frase ("ehhh crea...", "o sea haz...")
        while re.search(INITIAL_FILLERS, cleaned, flags=re.IGNORECASE):
            cleaned = re.sub(INITIAL_FILLERS, '', cleaned, flags=re.IGNORECASE).strip()

        # 4. Limpiar signos de puntuación iniciales sobrantes
        cleaned = re.sub(r'^[\s,.\-—–]+', '', cleaned).strip()

        # 5. Detección de cancelación voluntaria
        normalized_lower = cleaned.lower().strip(" .!?,;")
        if normalized_lower in CANCEL_PHRASES:
            return cleaned, False, f"Cancelación detectada ('{cleaned}')"

        # 6. Detección de alucinaciones comunes de Whisper o filtraciones de prompt
        hallucination_patterns = [
            r'transcripci[oó]n limpia en espa[ñn]ol',
            r'instrucciones de desarrollo para',
            r'subt[ií]tulos por la comunidad',
            r'amara\.org',
            r'gracias por ver',
            r'suscr[ií]bete',
            r'hasta el pr[oó]ximo video',
            r'hasta la pr[oó]xima',
        ]
        for pattern in hallucination_patterns:
            if re.search(pattern, normalized_lower):
                return cleaned, False, f"Alucinación de Whisper detectada ('{cleaned}')"

        # 7. Detección de titubeo incompleto (menos de 2 palabras con significado)
        words = [w for w in cleaned.split() if len(w) > 1]
        if len(words) < 2:
            return cleaned, False, f"Titubeo o frase incompleta ('{cleaned}')"

        # Capitalizar primera letra para presentación limpia
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned, True, "OK"
