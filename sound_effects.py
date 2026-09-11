"""
Módulo de efectos de sonido nativos para Windows (winsound).
Emite tonos acústicos para confirmar estados sin bloquear la ejecución.
"""
import threading
import sys
import config

def _play(frequency: int, duration: int):
    """Reproduce un tono en Windows si está habilitado."""
    if not config.SOUND_FEEDBACK_ENABLED:
        return
    if sys.platform == "win32":
        import winsound
        try:
            winsound.Beep(frequency, duration)
        except Exception:
            pass

def play_wake_detected():
    """Tono agudo rápido cuando se detecta la palabra clave o el atajo."""
    threading.Thread(target=lambda: _play(1200, 150), daemon=True).start()

def play_recording_stop():
    """Tono descendente suave cuando termina de grabar."""
    threading.Thread(target=lambda: _play(850, 120), daemon=True).start()

def play_success():
    """Tono alegre ascendente cuando se lanza la orden a Antigravity."""
    def _tone():
        _play(1000, 90)
        _play(1400, 140)
    threading.Thread(target=_tone, daemon=True).start()

def play_error():
    """Tono grave de advertencia."""
    threading.Thread(target=lambda: _play(400, 250), daemon=True).start()
