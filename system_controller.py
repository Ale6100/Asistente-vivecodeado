import os
import re
import time
import base64
import ctypes
import urllib.parse
import webbrowser
import subprocess
import threading
from datetime import datetime

import config
import sound_effects

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_LWIN = 0x5B
VK_D = 0x44
VK_MENU = 0x12
VK_F4 = 0x73

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES_ANIO = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

SEARCH_ENGINES = {
    "youtube": "https://www.youtube.com/results?search_query={query}",
    "google": "https://www.google.com/search?q={query}",
    "github": "https://github.com/search?q={query}",
    "mercadolibre": "https://listado.mercadolibre.com.ar/{query}",
    "mercado libre": "https://listado.mercadolibre.com.ar/{query}",
    "wikipedia": "https://es.wikipedia.org/wiki/{query}",
    "netflix": "https://www.netflix.com/search?q={query}",
    "spotify": "https://open.spotify.com/search/{query}",
    "twitter": "https://x.com/search?q={query}",
    "x": "https://x.com/search?q={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
}

QUICK_SITES = {
    "youtube": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "whatsapp": "https://web.whatsapp.com",
    "github": "https://github.com",
    "spotify": "https://open.spotify.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "mercadolibre": "https://www.mercadolibre.com.ar",
    "mercado libre": "https://www.mercadolibre.com.ar",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chatgpt.com",
}

QUICK_APPS = {
    "calculadora": "calc",
    "bloc de notas": "notepad",
    "bloc": "notepad",
    "notepad": "notepad",
    "terminal": "powershell",
    "explorador": "explorer",
}

def send_key_tap(vk_code: int):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    time.sleep(0.04)
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)

def send_key_combo(vk_mod: int, vk_key: int):
    ctypes.windll.user32.keybd_event(vk_mod, 0, 0, 0)
    time.sleep(0.04)
    ctypes.windll.user32.keybd_event(vk_key, 0, 0, 0)
    time.sleep(0.04)
    ctypes.windll.user32.keybd_event(vk_key, 0, 2, 0)
    time.sleep(0.04)
    ctypes.windll.user32.keybd_event(vk_mod, 0, 2, 0)

class SystemController:
    def __init__(self, speaker=None):
        self.speaker = speaker
        self.stopwatch_start_time = None
        self.active_timers = []

    def handle_command(self, text: str) -> tuple[bool, str, bool]:
        if not text:
            return False, "", False

        cleaned = text.strip()
        lower = cleaned.lower()

        if re.search(r'\b(basta|apagate|apágate|cerrar asistente|apagar asistente|adios|adiós|salir del asistente)\b', lower):
            return True, "Hasta luego. Cerrando asistente.", True

        if re.search(r'\b(modo discreto|silenciar voz|silencio total|muteate|mutéate|silenciate|silénciate|sin audio|sin voz|no hables|quedate mudo|quéditate mudo)\b', lower):
            config.TTS_ENABLED = False
            return True, "Modo discreto activado. Respuestas únicamente por texto.", False

        if re.search(r'\b(activar voz|modo hablado|desactivar silencio|hablar|desmuteate|desmutéate)\b', lower):
            config.TTS_ENABLED = True
            return True, "Voz activada.", False

        if re.search(r'\b(qué hora es|que hora es|la hora|dime la hora|decime la hora)\b', lower):
            now = datetime.now()
            hora_mensaje = f"Son las {now.hour}:{now.minute:02d}."
            return True, hora_mensaje, False

        if re.search(r'\b(qué fecha es|que fecha es|qué día es|que dia es|la fecha|dime la fecha|decime la fecha)\b', lower):
            now = datetime.now()
            dia = DIAS_SEMANA[now.weekday()]
            mes = MESES_ANIO[now.month - 1]
            fecha_mensaje = f"Hoy es {dia} {now.day} de {mes} de {now.year}."
            return True, fecha_mensaje, False

        if re.search(r'\b(captura de pantalla|sacar captura|sacá una captura|hacer captura|screenshot)\b', lower):
            ruta_captura = self._take_screenshot()
            if ruta_captura:
                return True, f"Captura de pantalla guardada en: {ruta_captura}", False
            return True, "No se pudo tomar la captura de pantalla.", False

        if re.search(r'\b(minimizar todo|mostrar escritorio|minimiza todo|minimizá todo|minimiza|minimizá|minimizar)\b', lower):
            subprocess.run(["powershell", "-NoProfile", "-Command", "(New-Object -ComObject Shell.Application).MinimizeAll()"], capture_output=True)
            return True, "Ventanas minimizadas.", False

        if re.search(r'\b(cerrar ventana|cerrar programa|cerrar archivo|cierra el programa|cerrá el programa)\b', lower):
            send_key_combo(VK_MENU, VK_F4)
            return True, "Ventana cerrada.", False

        if re.search(r'\b(minimizar ventana|minimiza la ventana|minimizá la ventana)\b', lower):
            send_key_combo(VK_MENU, 0x20)
            time.sleep(0.05)
            send_key_tap(ord('N'))
            return True, "Ventana minimizada.", False

        match_atajo = re.search(r'\batajo (\d)\b', lower)
        if match_atajo:
            num = int(match_atajo.group(1))
            if 1 <= num <= 9:
                send_key_combo(VK_LWIN, ord(str(num)))
                return True, f"Abriendo atajo {num}.", False

        if re.search(r'\b(mute|silenciar|mutear|desmutear|quitar mute)\b', lower):
            send_key_tap(VK_VOLUME_MUTE)
            return True, "Silencio alternado.", False

        if re.search(r'\b(subir volumen|sube el volumen|subí el volumen|más volumen)\b', lower):
            for _ in range(5):
                send_key_tap(VK_VOLUME_UP)
                time.sleep(0.02)
            return True, "Volumen aumentado.", False

        if re.search(r'\b(bajar volumen|baja el volumen|bajá el volumen|menos volumen)\b', lower):
            for _ in range(5):
                send_key_tap(VK_VOLUME_DOWN)
                time.sleep(0.02)
            return True, "Volumen reducido.", False

        match_vol = re.search(r'\bvolumen al (\d{1,3})\b', lower)
        if match_vol:
            pct = int(match_vol.group(1))
            self._set_volume_percentage(pct)
            return True, f"Volumen ajustado al {pct} por ciento.", False

        if re.search(r'\b(iniciar|iniciá|comenzar|comenzá) cronómetro\b', lower):
            self.stopwatch_start_time = time.time()
            return True, "Cronómetro iniciado.", False

        if re.search(r'\b(detener|detené|parar|pará) cronómetro\b', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False
            transcurrido = int(time.time() - self.stopwatch_start_time)
            self.stopwatch_start_time = None
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"Cronómetro detenido en {minutos} minutos y {segundos} segundos.", False
            return True, f"Cronómetro detenido en {segundos} segundos.", False

        if re.search(r'\b(tiempo del cronómetro|cuánto va del cronómetro|cuanto va del cronometro)\b', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False
            transcurrido = int(time.time() - self.stopwatch_start_time)
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"El cronómetro lleva {minutos} minutos y {segundos} segundos.", False
            return True, f"El cronómetro lleva {segundos} segundos.", False

        match_alarm = re.search(r'\b(?:alarma|temporizador|recordatorio|recuérdame|recordame)\b.*?\b(\d+)\s*(minuto|minutos|segundo|segundos)\b', lower)
        if match_alarm:
            qty = int(match_alarm.group(1))
            unit = match_alarm.group(2)
            total_seconds = qty * 60 if "minuto" in unit else qty
            self._schedule_alarm(total_seconds, qty, unit)
            return True, f"Alarma programada para dentro de {qty} {unit}.", False

        match_search_2 = re.search(r'\b(?:abrir|abrime|abrí|abre)\s+(youtube|netflix|google|github|mercado libre|mercadolibre|wikipedia|spotify|twitter|reddit)\s+y\s+(?:buscar|buscame|buscá)\s+(.+)\b', lower)
        if match_search_2:
            service = match_search_2.group(1).lower().strip()
            query = match_search_2.group(2).strip()
            self._open_search(service, query)
            return True, f"Buscando '{query}' en {service.title()}.", False

        match_search_1 = re.search(r'\b(?:buscar|buscame|buscá)\s+(.+?)\s+en\s+(youtube|netflix|google|github|mercado libre|mercadolibre|wikipedia|spotify|twitter|reddit)\b', lower)
        if match_search_1:
            query = match_search_1.group(1).strip()
            service = match_search_1.group(2).lower().strip()
            self._open_search(service, query)
            return True, f"Buscando '{query}' en {service.title()}.", False

        match_open = re.search(r'\b(?:abrir|abrime|abrí|abre)\s+([a-zA-Z0-9áéíóúÁÉÍÓÚ\s]+)\b', lower)
        if match_open:
            target = match_open.group(1).strip()
            if target in QUICK_SITES:
                webbrowser.open(QUICK_SITES[target])
                return True, f"Abriendo {target.title()}.", False
            if target in QUICK_APPS:
                subprocess.Popen([QUICK_APPS[target]], shell=True)
                return True, f"Abriendo {target.title()}.", False

        if re.search(r'\b(clima|temperatura|tiempo meteorológico)\b', lower):
            webbrowser.open("https://www.google.com/search?q=clima+hoy")
            return True, "Abriendo el reporte del clima en Google.", False

        return False, "", False

    def _open_search(self, service: str, query: str):
        template = SEARCH_ENGINES.get(service, "https://www.google.com/search?q={query}")
        url = template.format(query=urllib.parse.quote(query))
        webbrowser.open(url)

    def _take_screenshot(self) -> str:
        folder = os.path.abspath("screenshots")
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(folder, f"captura_{timestamp}.png")

        script = f"""
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
$bmp.Save('{target_file}')
$g.Dispose()
$bmp.Dispose()
"""
        try:
            b64 = base64.b64encode(script.encode('utf-16le')).decode('ascii')
            subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", b64], capture_output=True, check=True)
            if os.path.exists(target_file):
                return target_file
        except Exception:
            pass
        return ""

    def _set_volume_percentage(self, percentage: int):
        clamped = max(0, min(100, percentage))
        for _ in range(50):
            send_key_tap(VK_VOLUME_DOWN)
            time.sleep(0.005)
        steps_up = round(clamped / 2)
        for _ in range(steps_up):
            send_key_tap(VK_VOLUME_UP)
            time.sleep(0.005)

    def _schedule_alarm(self, seconds: int, qty: int, unit: str):
        def _alarm_callback():
            sound_effects.play_wake_detected()
            time.sleep(0.25)
            sound_effects.play_success()
            msg = f"¡Atención! Ha finalizado la alarma de {qty} {unit}."
            print(f"\n⏰ [bold yellow]{msg}[/bold yellow]\n")
            if getattr(config, "TTS_ENABLED", True) and self.speaker:
                self.speaker.speak(msg)

        timer = threading.Timer(seconds, _alarm_callback)
        timer.daemon = True
        timer.start()
        self.active_timers.append(timer)
