"""
Módulo de Text-To-Speech (Voz de Salida) para el Asistente Virtual.
Utiliza Microsoft Edge Neural TTS (alta fidelidad humana) con control de velocidad y fallback local a Windows SAPI5.
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import re
import sys
import asyncio
import tempfile
import threading
import subprocess

import config

try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

def clean_markdown_for_speech(text: str) -> str:
    """
    Limpia etiquetas de Markdown y bloques de código para que la lectura
    sea 100% natural al oído.
    """
    if not text:
        return ""

    # Reemplazar bloques de código ```...``` por una mención breve
    cleaned = re.sub(r'```[\s\S]*?```', ' Código generado en los archivos. ', text)
    # Reemplazar código inline `...`
    cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
    # Reemplazar enlaces [texto](url) por solo el texto
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
    # Eliminar encabezados #, ##, etc.
    cleaned = re.sub(r'#+\s*', '', cleaned)
    # Eliminar negritas, cursivas * o _
    cleaned = re.sub(r'[*_~]+', '', cleaned)
    # Eliminar citas >
    cleaned = re.sub(r'^\s*>\s*', '', cleaned, flags=re.MULTILINE)
    # Limpiar saltos de línea repetidos
    cleaned = re.sub(r'\n+', '. ', cleaned)
    # Limpiar espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Limitar longitud para evitar discursos excesivamente largos por voz
    if len(cleaned) > 500:
        cleaned = cleaned[:480].rsplit('.', 1)[0] + ". Te dejé los detalles completos en la consola."

    return cleaned

class TTSSpeaker:
    def __init__(self):
        self.voice = getattr(config, "TTS_VOICE", "es-ES-AlvaroNeural")
        self.rate = getattr(config, "TTS_RATE", "+25%")
        self.is_speaking = False

    def speak(self, text: str):
        """Sintetiza y reproduce el texto por los altavoces de forma síncrona."""
        if not getattr(config, "TTS_ENABLED", True) or not text:
            return

        speech_text = clean_markdown_for_speech(text)
        if not speech_text:
            return

        self.is_speaking = True
        try:
            asyncio.run(self._speak_edge(speech_text))
        except Exception:
            self._speak_windows_sapi(speech_text)
        finally:
            self.is_speaking = False

    async def _speak_edge(self, text: str):
        """Descarga el audio de Edge-TTS con velocidad aumentada y lo reproduce."""
        import edge_tts

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        try:
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            await communicate.save(temp_path)

            if PYGAME_AVAILABLE:
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.06)
                pygame.mixer.music.unload()
            else:
                cmd = f"(New-Object Media.SoundPlayer '{temp_path}').PlaySync()"
                subprocess.run(["powershell", "-c", cmd], check=True)
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _speak_windows_sapi(self, text: str):
        """Fallback offline mediante el sintetizador de voz integrado de Windows."""
        try:
            escaped = text.replace("'", "''").replace('"', '`"')
            ps_cmd = (
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$synth.Rate = 2; "
                f"$synth.Speak('{escaped}')"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True)
        except Exception:
            pass
