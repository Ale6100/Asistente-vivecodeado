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
from rich.console import Console

import config
import sound_effects

console = Console()

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
    "disney plus": "https://www.disneyplus.com/search?q={query}",
    "disney+": "https://www.disneyplus.com/search?q={query}",
    "disney": "https://www.disneyplus.com/search?q={query}",
    "spotify": "https://open.spotify.com/search/{query}",
    "twitter": "https://x.com/search?q={query}",
    "x": "https://x.com/search?q={query}",
    "reddit": "https://www.reddit.com/search/?q={query}",
}

SEMANTIC_QUERY_PATTERN = re.compile(
    r'\b(?:más|mas|mejor|mejores|último|ultimo|últimos|ultimos|nuevo|nuevos|reciente|recientes|'
    r'barato|baratos|caro|caros|cuál|cual|cuáles|cuales|quién|quien|cómo|como|por qué|porque|'
    r'qué|que|diferencia|vs|versus|top|ranking|tutorial|explicación|explicacion|resumen|'
    r'noticia|noticias|visitas|reproducciones|popular|populares|famoso|famosa|famosos|famosas)\b',
    re.IGNORECASE
)

QUICK_SITES = {
    "youtube": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "disney plus": "https://www.disneyplus.com",
    "disney+": "https://www.disneyplus.com",
    "disney": "https://www.disneyplus.com",
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

SEARCH_VERBS_PATTERN = r'(?:buscar|buscame|búscame|buscá|busca|busque|búsqueme|googlear|googleá|googlea)'
OPEN_VERBS_PATTERN = r'(?:abrir|abrime|ábreme|abrí|abre|abra)'
SEARCH_SERVICES_PATTERN = r'(youtube|netflix|disney plus|disney\+|disney|google|github|mercado libre|mercadolibre|wikipedia|spotify|twitter|reddit)'
VIDEO_VERBS_PATTERN = r'(?:mostrar|mostrame|muéstrame|mostrá|muestra|muestre|abrir|abrime|ábreme|abrí|abre|abra|ver|buscar|buscame|búscame|buscá|busca|busque|reproducir|reproduce|reproduzca|reproducí|poné|pone|pon|ponga|play|poner|ponme|poneme)'
MEDIA_TYPES_PATTERN = r'(video|vídeo|canción|cancion|tema|trailer|tráiler|música|musica)'
COMMAND_PREFIX_PATTERN = r'^(?:por\s+favor\s+|podrías\s+|podrias\s+|podés\s+|podes\s+|che\s+|asistente\s+)?'
EXPLANATORY_PREFACES_PATTERN = re.compile(
    r'^(?:noto\b|veo\b|siento\b|cuando\b|si\b|por\s+ejemplo\b|ejemplo\b|te\s+(?:decía|decia|dije|estaba|quiero|quería|queria)\b|'
    r'por\s+qué\b|porque\b|¿por\s+qué\b|explicar\b|no\s+es\s+necesario\b|no\s+hace\s+falta\b|acabo\s+de\b|'
    r'notas\b|viste\b|sabes\b|sabés\b|te\s+pregunto\b|pregunta\b|consulta\b)',
    re.IGNORECASE
)

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

def open_url_native(url: str):
    try:
        user32 = ctypes.windll.user32
        hdesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)
            ctypes.windll.shell32.ShellExecuteW(None, "open", url, None, None, 1)
            return
    except Exception:
        pass
    try:
        os.startfile(url)
    except Exception:
        webbrowser.open(url)

def take_screenshot() -> str:
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

class SystemController:
    def __init__(self, speaker=None):
        self.speaker = speaker
        self.stopwatch_start_time = None
        self.active_timers = []
        self.last_action = None

    def handle_command(self, text: str) -> tuple[bool, str, bool, bool]:
        if not text:
            return False, "", False, False

        cleaned = text.strip()
        lower = cleaned.lower().rstrip(" \t\n\r.,!?:;\"'")

        if EXPLANATORY_PREFACES_PATTERN.search(lower):
            return False, "", False, False

        if re.search(r'\b(basta|apagate|apágate|cerrar asistente|apagar asistente|adios|adiós|salir del asistente)\b', lower):
            return True, "Hasta luego. Cerrando asistente.", True, False

        if re.search(r'\b(modo discreto|silenciar voz|silencio total|muteate|mutéate|silenciate|silénciate|sin audio|sin voz|no hables|quedate mudo|quéditate mudo)\b', lower):
            config.TTS_ENABLED = False
            return True, "Modo discreto activado. Respuestas únicamente por texto.", False, False

        if re.search(r'\b(activar voz|modo hablado|desactivar silencio|hablar|desmuteate|desmutéate)\b', lower):
            config.TTS_ENABLED = True
            return True, "Voz activada.", False, True

        if re.search(r'\b(qué hora es|que hora es|la hora|dime la hora|decime la hora)\b', lower):
            now = datetime.now()
            hora_mensaje = f"Son las {now.hour}:{now.minute:02d}."
            return True, hora_mensaje, False, True

        if re.search(r'\b(qué fecha es|que fecha es|qué día es|que dia es|la fecha|dime la fecha|decime la fecha)\b', lower):
            now = datetime.now()
            dia = DIAS_SEMANA[now.weekday()]
            mes = MESES_ANIO[now.month - 1]
            fecha_mensaje = f"Hoy es {dia} {now.day} de {mes} de {now.year}."
            return True, fecha_mensaje, False, True

        if re.search(r'\b(así otra|asi otra|otra|otra más|otro más|sacá otra|saca otra|hacé otra|hace otra|otra captura|repetir captura)\b', lower):
            if self.last_action == "screenshot":
                ruta_captura = take_screenshot()
                if ruta_captura:
                    return True, f"Captura de pantalla guardada en: {ruta_captura}", False, False
                return True, "No se pudo tomar la captura de pantalla.", False, False
            if self.last_action == "volume_up":
                for _ in range(5):
                    send_key_tap(VK_VOLUME_UP)
                    time.sleep(0.02)
                return True, "Volumen aumentado.", False, False
            if self.last_action == "volume_down":
                for _ in range(5):
                    send_key_tap(VK_VOLUME_DOWN)
                    time.sleep(0.02)
                return True, "Volumen reducido.", False, False

        if re.search(r'\b(captura de pantalla|sacar captura|sacá una captura|hacer captura|screenshot)\b', lower):
            self.last_action = "screenshot"
            ruta_captura = take_screenshot()
            if ruta_captura:
                return True, f"Captura de pantalla guardada en: {ruta_captura}", False, False
            return True, "No se pudo tomar la captura de pantalla.", False, False

        if re.search(r'\b(minimizar todo|mostrar escritorio|minimiza todo|minimizá todo|minimiza|minimizá|minimizar)\b', lower):
            subprocess.run(["powershell", "-NoProfile", "-Command", "(New-Object -ComObject Shell.Application).MinimizeAll()"], capture_output=True)
            return True, "Ventanas minimizadas.", False, False

        if re.search(r'\b(cerrar ventana|cerrar programa|cerrar archivo|cierra el programa|cerrá el programa)\b', lower):
            send_key_combo(VK_MENU, VK_F4)
            return True, "Ventana cerrada.", False, False

        if re.search(r'\b(minimizar ventana|minimiza la ventana|minimizá la ventana)\b', lower):
            send_key_combo(VK_MENU, 0x20)
            time.sleep(0.05)
            send_key_tap(ord('N'))
            return True, "Ventana minimizada.", False, False

        match_atajo = re.search(r'\batajo (\d)\b', lower)
        if match_atajo:
            num = int(match_atajo.group(1))
            if 1 <= num <= 9:
                send_key_combo(VK_LWIN, ord(str(num)))
                return True, f"Abriendo atajo {num}.", False, False

        if re.search(r'\b(mute|silenciar|mutear|desmutear|quitar mute)\b', lower):
            send_key_tap(VK_VOLUME_MUTE)
            return True, "Silencio alternado.", False, False

        if re.search(r'\b(subir volumen|sube el volumen|subí el volumen|más volumen)\b', lower):
            self.last_action = "volume_up"
            for _ in range(5):
                send_key_tap(VK_VOLUME_UP)
                time.sleep(0.02)
            return True, "Volumen aumentado.", False, False

        if re.search(r'\b(bajar volumen|baja el volumen|bajá el volumen|menos volumen)\b', lower):
            self.last_action = "volume_down"
            for _ in range(5):
                send_key_tap(VK_VOLUME_DOWN)
                time.sleep(0.02)
            return True, "Volumen reducido.", False, False

        match_vol = re.search(r'\bvolumen al (\d{1,3})\b', lower)
        if match_vol:
            pct = int(match_vol.group(1))
            self._set_volume_percentage(pct)
            return True, f"Volumen ajustado al {pct} por ciento.", False, False

        if re.search(r'\b(iniciar|iniciá|comenzar|comenzá) cronómetro\b', lower):
            self.stopwatch_start_time = time.time()
            return True, "Cronómetro iniciado.", False, False

        if re.search(r'\b(detener|detené|parar|pará) cronómetro\b', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False, True
            transcurrido = int(time.time() - self.stopwatch_start_time)
            self.stopwatch_start_time = None
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"Cronómetro detenido en {minutos} minutos y {segundos} segundos.", False, True
            return True, f"Cronómetro detenido en {segundos} segundos.", False, True

        if re.search(r'\b(tiempo del cronómetro|cuánto va del cronómetro|cuanto va del cronometro)\b', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False, True
            transcurrido = int(time.time() - self.stopwatch_start_time)
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"El cronómetro lleva {minutos} minutos y {segundos} segundos.", False, True
            return True, f"El cronómetro lleva {segundos} segundos.", False, True

        match_alarm = re.search(r'\b(?:alarma|temporizador|recordatorio|recuérdame|recordame)\b.*?\b(\d+)\s*(minuto|minutos|segundo|segundos)\b', lower)
        if match_alarm:
            qty = int(match_alarm.group(1))
            unit = match_alarm.group(2)
            total_seconds = qty * 60 if "minuto" in unit else qty
            self._schedule_alarm(total_seconds, qty, unit)
            return True, f"Alarma programada para dentro de {qty} {unit}.", False, False

        match_search_open = re.match(COMMAND_PREFIX_PATTERN + OPEN_VERBS_PATTERN + r'\s+' + SEARCH_SERVICES_PATTERN + r'\s+y\s+' + SEARCH_VERBS_PATTERN + r'\s+(.+)$', lower)
        if match_search_open:
            service = match_search_open.group(1).lower().strip()
            raw_target = match_search_open.group(2).strip(" \t\n\r.,!?:;\"'")
            query = re.sub(r'^(?:el|la|los|las|un|una|unos|unas)\s+', '', raw_target, flags=re.IGNORECASE).strip()
            if not SEMANTIC_QUERY_PATTERN.search(query):
                self._open_search(service, query)
                return True, f"Buscando '{query}' en {service.title()}.", False, False

        match_search_query_in_service = re.match(COMMAND_PREFIX_PATTERN + SEARCH_VERBS_PATTERN + r'\s+(.+?)\s+en\s+' + SEARCH_SERVICES_PATTERN + r'$', lower)
        if match_search_query_in_service:
            raw_target = match_search_query_in_service.group(1).strip(" \t\n\r.,!?:;\"'")
            service = match_search_query_in_service.group(2).lower().strip()
            query = re.sub(r'^(?:el|la|los|las|un|una|unos|unas)\s+', '', raw_target, flags=re.IGNORECASE).strip()
            if not SEMANTIC_QUERY_PATTERN.search(query):
                self._open_search(service, query)
                return True, f"Buscando '{query}' en {service.title()}.", False, False

        match_search_service_query = re.match(COMMAND_PREFIX_PATTERN + SEARCH_VERBS_PATTERN + r'\s+en\s+' + SEARCH_SERVICES_PATTERN + r'\s+(.+)$', lower)
        if match_search_service_query:
            service = match_search_service_query.group(1).lower().strip()
            raw_target = match_search_service_query.group(2).strip(" \t\n\r.,!?:;\"'")
            query = re.sub(r'^(?:el|la|los|las|un|una|unos|unas)\s+', '', raw_target, flags=re.IGNORECASE).strip()
            if not SEMANTIC_QUERY_PATTERN.search(query):
                self._open_search(service, query)
                return True, f"Buscando '{query}' en {service.title()}.", False, False

        lower_filtered = re.sub(r'^.*?\b(?:no\s+se\s+(?:abrió|abrio|mostró|mostro)|no\s+abriste|no\s+lo\s+abriste)[^,.]*[,.]?\s*', '', lower)

        match_video = re.match(COMMAND_PREFIX_PATTERN + VIDEO_VERBS_PATTERN + r'\b.*?\b(?:el\s+|la\s+|un\s+|una\s+)?' + MEDIA_TYPES_PATTERN + r'(?:\s+(?:de|con|sobre)\b)?\s*(.+)?$', lower_filtered)
        if match_video:
            media_type = match_video.group(1).lower()
            raw = (match_video.group(2) or "").strip(" \t\n\r.,!?:;\"'")
            raw = re.sub(r'\s+(?:en|por)\s+youtube\b', '', raw, flags=re.IGNORECASE).strip()
            raw = re.sub(r'\bmi\s+dudev\b', 'midudev', raw, flags=re.IGNORECASE)
            raw = re.sub(r'^(?:un|uno|una|el|la|los|las|de|sobre|con)\s+', '', raw, flags=re.IGNORECASE).strip()
            if not raw or raw in ("video", "vídeo", "algo", "cancion", "canción", "tema", "música", "musica"):
                self._open_search("youtube", "")
                return True, "Abriendo YouTube.", False, False
            if media_type in ("trailer", "tráiler") and "trailer" not in raw and "tráiler" not in raw:
                target_query = f"trailer {raw}".strip()
            else:
                target_query = raw
            if not SEMANTIC_QUERY_PATTERN.search(target_query):
                self._open_search("youtube", target_query)
                return True, f"Buscando '{target_query}' en YouTube.", False, False

        match_generic_search = re.match(COMMAND_PREFIX_PATTERN + SEARCH_VERBS_PATTERN + r'\s+(.+)$', lower)
        if match_generic_search:
            raw_query = match_generic_search.group(1).strip(" \t\n\r.,!?:;\"'")
            raw_query = re.sub(r'^(?:en\s+google\s+|de\s+|sobre\s+)', '', raw_query, flags=re.IGNORECASE).strip()
            if not any(k in raw_query for k in ["archivo", "función", "bug", "código", "codigo", "commit"]) and not SEMANTIC_QUERY_PATTERN.search(raw_query):
                self._open_search("google", raw_query)
                return True, f"Buscando '{raw_query}' en Google.", False, False

        match_open = re.match(COMMAND_PREFIX_PATTERN + OPEN_VERBS_PATTERN + r'\s+([a-zA-Z0-9áéíóúÁÉÍÓÚ\s\+]+)$', lower)
        if match_open:
            target = match_open.group(1).strip()
            if target in QUICK_SITES:
                open_url_native(QUICK_SITES[target])
                return True, f"Abriendo {target.title()}.", False, False
            if target in QUICK_APPS:
                subprocess.Popen([QUICK_APPS[target]], shell=True)
                return True, f"Abriendo {target.title()}.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:el\s+)?(clima|temperatura|tiempo meteorológico)\b', lower):
            open_url_native("https://www.google.com/search?q=clima+hoy")
            return True, "Abriendo el reporte del clima en Google.", False, False

        return False, "", False, False

    def _open_search(self, service: str, query: str):
        if not query:
            url = QUICK_SITES.get(service, f"https://www.{service}.com")
        else:
            template = SEARCH_ENGINES.get(service, "https://www.google.com/search?q={query}")
            url = template.format(query=urllib.parse.quote(query))
        open_url_native(url)

    def _take_screenshot(self) -> str:
        return take_screenshot()

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
            console.print(f"\n⏰ [bold yellow]{msg}[/bold yellow]\n")
            if getattr(config, "TTS_ENABLED", True) and self.speaker:
                self.speaker.speak(msg)

        timer = threading.Timer(seconds, _alarm_callback)
        timer.daemon = True
        timer.start()
        self.active_timers.append(timer)
