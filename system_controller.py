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
    "discord": r'explorer "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Discord.lnk"',
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
    r'notas\b|viste\b|sabes\b|sabés\b|te\s+pregunto\b|pregunta\b|consulta\b|'
    r'en\s+realidad\b|creo\b|creo\s+que\b|me\s+parece\b|estaba\s+pensando\b|o\s+sea\b|por\s+casualidad\b|'
    r'te\s+quería\s+preguntar\b|ayudame\b|ayúdame\b|decime\b|mostrame\b|muéstrame\b|'
    r'no\s+quiero\b|quiero\s+saber\b|vos\s+podrías\b|vos\s+podrias\b|vos\s+podés\b|vos\s+podes\b|'
    r'qué\s+onda\b|que\s+onda\b|cómo\s+es\b|como\s+es\b)',
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base_dir, "screenshots")
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

def sort_desktop_alphabetically() -> bool:
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(base_dir, "tools", "SortDesktop.exe")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(base_dir, "SortDesktop.exe")
        if os.path.exists(exe_path):
            subprocess.run([exe_path], capture_output=True, check=True)
            return True
    except Exception:
        pass
    return False

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

        # Si el texto es una pregunta o una frase reflexiva/conversacional, derivar a la IA
        if ('?' in cleaned or '¿' in cleaned) and not re.match(COMMAND_PREFIX_PATTERN + r'(?:¿?\s*(?:qué|que)\s+hora\s+es\??|¿?\s*(?:qué|que)\s+(?:fecha|día|dia)\s+es\??)$', lower):
            return False, "", False, False

        # Si es una frase larga (más de 9 palabras) que no sea un comando explícito estructurado de búsqueda o multimedia
        words = lower.split()
        if len(words) > 9 and not re.match(COMMAND_PREFIX_PATTERN + r'(?:buscar|reproducir|poner|poné)\b', lower):
            return False, "", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:basta|apagate|apágate|cerrar\s+asistente|apagar\s+asistente|adios|adiós|salir\s+del\s+asistente)$', lower):
            return True, "Hasta luego. Cerrando asistente.", True, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:modo\s+discreto|silenciar\s+voz|silencio\s+total|muteate|mutéate|silenciate|silénciate|sin\s+audio|sin\s+voz|no\s+hables|quedate\s+mudo|quéditate\s+mudo)$', lower):
            config.TTS_ENABLED = False
            return True, "Modo discreto activado. Respuestas únicamente por texto.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:activar\s+voz|modo\s+hablado|desactivar\s+silencio|hablar|desmuteate|desmutéate)$', lower):
            config.TTS_ENABLED = True
            return True, "Voz activada.", False, True

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:qué\s+hora\s+es|que\s+hora\s+es|la\s+hora|dime\s+la\s+hora|decime\s+la\s+hora)$', lower):
            now = datetime.now()
            hora_mensaje = f"Son las {now.hour}:{now.minute:02d}."
            return True, hora_mensaje, False, True

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:qué\s+fecha\s+es|que\s+fecha\s+es|qué\s+día\s+es|que\s+dia\s+es|la\s+fecha|dime\s+la\s+fecha|decime\s+la\s+fecha)$', lower):
            now = datetime.now()
            dia = DIAS_SEMANA[now.weekday()]
            mes = MESES_ANIO[now.month - 1]
            fecha_mensaje = f"Hoy es {dia} {now.day} de {mes} de {now.year}."
            return True, fecha_mensaje, False, True

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:así\s+otra|asi\s+otra|otra|otra\s+más|otro\s+más|sacá\s+otra|saca\s+otra|hacé\s+otra|hace\s+otra|otra\s+captura|repetir\s+captura)$', lower):
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

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:(?:sacar|sacá|saca|hacer|hacé|hace|tomar|tomá|toma)\s+(?:una\s+)?captura(?:\s+de\s+pantalla)?(?:\s+del?\s+escritorio)?|captura\s+de\s+pantalla|captura|screenshot)$', lower):
            self.last_action = "screenshot"
            ruta_captura = take_screenshot()
            if ruta_captura:
                return True, f"Captura de pantalla guardada en: {ruta_captura}", False, False
            return True, "No se pudo tomar la captura de pantalla.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:minimizar\s+todo|mostrar\s+escritorio|minimiza\s+todo|minimizá\s+todo|mostrar\s+el\s+escritorio)$', lower):
            subprocess.run(["powershell", "-NoProfile", "-Command", "(New-Object -ComObject Shell.Application).MinimizeAll()"], capture_output=True)
            return True, "Ventanas minimizadas.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:ordenar|ordená|ordena|ordenes|ordenés)\s+(?:los\s+)?(?:elementos|iconos|archivos)?\s*(?:de(?:l|\s+mi)\s+)?escritorio$', lower):
            if sort_desktop_alphabetically():
                return True, "Elementos del escritorio ordenados en orden alfabético.", False, False
            return True, "No se pudieron ordenar los elementos del escritorio.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:cerrar\s+ventana|cerrar\s+programa|cerrar\s+archivo|cierra\s+el\s+programa|cerrá\s+el\s+programa|cerrar\s+esta\s+ventana)$', lower):
            send_key_combo(VK_MENU, VK_F4)
            return True, "Ventana cerrada.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:minimizar\s+ventana|minimiza\s+la\s+ventana|minimizá\s+la\s+ventana)$', lower):
            send_key_combo(VK_MENU, 0x20)
            time.sleep(0.05)
            send_key_tap(ord('N'))
            return True, "Ventana minimizada.", False, False

        match_atajo = re.match(COMMAND_PREFIX_PATTERN + r'atajo\s+(\d)$', lower)
        if match_atajo:
            num = int(match_atajo.group(1))
            if 1 <= num <= 9:
                send_key_combo(VK_LWIN, ord(str(num)))
                return True, f"Abriendo atajo {num}.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:mute|silenciar|mutear|desmutear|quitar\s+mute)$', lower):
            send_key_tap(VK_VOLUME_MUTE)
            return True, "Silencio alternado.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:subir\s+volumen|sube\s+el\s+volumen|subí\s+el\s+volumen|más\s+volumen)$', lower):
            self.last_action = "volume_up"
            for _ in range(5):
                send_key_tap(VK_VOLUME_UP)
                time.sleep(0.02)
            return True, "Volumen aumentado.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:bajar\s+volumen|baja\s+el\s+volumen|bajá\s+el\s+volumen|menos\s+volumen)$', lower):
            self.last_action = "volume_down"
            for _ in range(5):
                send_key_tap(VK_VOLUME_DOWN)
                time.sleep(0.02)
            return True, "Volumen reducido.", False, False

        match_vol = re.match(COMMAND_PREFIX_PATTERN + r'(?:poner\s+|poné\s+|ajustar\s+)?volumen\s+al\s+(\d{1,3})%?$', lower)
        if match_vol:
            pct = int(match_vol.group(1))
            self._set_volume_percentage(pct)
            return True, f"Volumen ajustado al {pct} por ciento.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:iniciar|iniciá|comenzar|comenzá)\s+cronómetro$', lower):
            self.stopwatch_start_time = time.time()
            return True, "Cronómetro iniciado.", False, False

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:detener|detené|parar|pará)\s+cronómetro$', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False, True
            transcurrido = int(time.time() - self.stopwatch_start_time)
            self.stopwatch_start_time = None
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"Cronómetro detenido en {minutos} minutos y {segundos} segundos.", False, True
            return True, f"Cronómetro detenido en {segundos} segundos.", False, True

        if re.match(COMMAND_PREFIX_PATTERN + r'(?:tiempo\s+del\s+cronómetro|cuánto\s+va\s+del\s+cronómetro|cuanto\s+va\s+del\s+cronometro)$', lower):
            if self.stopwatch_start_time is None:
                return True, "El cronómetro no está iniciado.", False, True
            transcurrido = int(time.time() - self.stopwatch_start_time)
            minutos = transcurrido // 60
            segundos = transcurrido % 60
            if minutos > 0:
                return True, f"El cronómetro lleva {minutos} minutos y {segundos} segundos.", False, True
            return True, f"El cronómetro lleva {segundos} segundos.", False, True

        match_alarm = re.match(COMMAND_PREFIX_PATTERN + r'(?:poner\s+|poné\s+|iniciar\s+|programar\s+)?(?:una\s+)?(?:alarma|temporizador|recordatorio)\s+(?:de|para\s+dentro\s+de)?\s*(\d+)\s*(minuto|minutos|segundo|segundos)$', lower)
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
