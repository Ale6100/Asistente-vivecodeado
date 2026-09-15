import sys
import os
import re
import shutil
import subprocess
import webbrowser
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
import sound_effects
import screen_reader
from tts_speaker import TTSSpeaker
from system_controller import open_url_native, take_screenshot

console = Console()

class AgyLauncher:
    def __init__(self):
        self.agy_cmd = config.AGY_COMMAND
        self.speaker = TTSSpeaker()
        self.has_active_conversation = False
        self.action_history = []

        if config.DEFAULT_PROJECT_DIR and os.path.isdir(config.DEFAULT_PROJECT_DIR):
            self.working_directory = os.path.abspath(config.DEFAULT_PROJECT_DIR)
        else:
            self.working_directory = os.getcwd()

        if not shutil.which(self.agy_cmd):
            console.print(f"[yellow]⚠️ Advertencia: No se encontró '{self.agy_cmd}' en el PATH del sistema.[/yellow]")

    def record_system_action(self, instruction: str, result_message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.action_history.append({
            "time": timestamp,
            "instruction": instruction,
            "result": result_message
        })
        if len(self.action_history) > 10:
            self.action_history.pop(0)

    def reset_conversation(self):
        self.has_active_conversation = False
        self.action_history.clear()

    def set_working_directory(self, new_dir: str) -> tuple[bool, str]:
        clean_path = new_dir.strip().strip('"').strip("'")
        expanded = os.path.abspath(os.path.expanduser(clean_path))
        if os.path.isdir(expanded):
            if self.working_directory != expanded:
                self.reset_conversation()
            self.working_directory = expanded
            return True, self.working_directory
        return False, f"La ruta '{clean_path}' no existe o no es una carpeta válida."

    def execute_prompt(self, prompt: str):
        if not prompt or not prompt.strip():
            return

        if not shutil.which(self.agy_cmd):
            error_message = (
                f"No se encontró el comando '{self.agy_cmd}' en el PATH del sistema. "
                "Verifica que Antigravity CLI esté instalado y disponible en la terminal."
            )
            console.print(f"[bold red]❌ {error_message}[/bold red]")
            sound_effects.play_error()
            if getattr(config, "TTS_ENABLED", True):
                self.speaker.speak("No se encontró el comando de Antigravity en el sistema.")
            return

        history_context = ""
        if self.action_history:
            recent_items = [
                f"- [{item['time']}] El usuario pidió: \"{item['instruction']}\" -> Acción ejecutada: {item['result']}"
                for item in self.action_history[-5:]
            ]
            history_context = (
                "\n\nAcciones recientes del sistema ejecutadas localmente en esta sesión por el asistente:\n"
                + "\n".join(recent_items)
                + "\n"
            )

        voice_context = (
            "[CONSIGNA DE CONTEXTO DEL SISTEMA]: "
            "El usuario se está comunicando contigo mediante voz y micrófono como su asistente virtual mientras trabaja en su computadora. "
            f"Carpeta de trabajo actual: '{self.working_directory}'. "
            "Tu respuesta será sintetizada en audio (TTS) para que el usuario la escuche mientras se concentra en su trabajo. "
            f"{history_context}"
            "Directrices esenciales: "
            "1. Para tareas mecánicas o de apertura directa (abrir páginas web, búsquedas en sitios específicos, abrir apps, multimedia, capturas de pantalla, etc.): incluye al final en su propia línea la directiva `[ACTION: OPEN_URL <url>]`, `[ACTION: OPEN_APP <comando>]` o `[ACTION: SCREENSHOT]`. En estas tareas mecánicas mantén tu mensaje muy breve ya que la confirmación visual y auditiva es suficiente. "
            "2. Para preguntas, explicaciones, conceptos técnicos, dudas o cuando el usuario pida explicaciones: responde con claridad y de forma completa. Tu respuesta será leída por voz en su totalidad. "
            "3. Para desarrollo: ejecuta las acciones reales (crear/editar archivos, git, comandos) en la carpeta de trabajo y resume el resultado de forma clara. "
            "4. No incluyas bloques de código markdown en el texto conversacional para que la síntesis de voz sea fluida y natural al oído. "
            "5. Limpieza estricta de temporales: cualquier archivo, captura de pantalla, script o recurso efímero creado para resolver una consulta o análisis debe ser eliminado inmediatamente al terminar su uso, sin dejar basura residual en el disco. "
            "6. Autonomía resolutiva proactiva: Nunca respondas con una negativa ni digas que no puedes hacer algo o que no está preprogramado si es técnicamente viable resolverlo. Crea al vuelo los scripts temporales, utilidades o capturas necesarias para obtener información o ejecutar la acción, procesa los resultados y elimínalos inmediatamente al finalizar sin dejar basura residual. "
            "\n\nInstrucción del usuario:\n"
        )

        temp_visual_file = None
        screen_context = ""

        if screen_reader.is_screen_inspection_request(prompt):
            with console.status("[bold cyan]👁️ Analizando pantalla...[/bold cyan]", spinner="dots"):
                mode, content, window_title = screen_reader.inspect_screen_for_prompt(prompt)
                if mode == "ocr":
                    screen_context = (
                        f"\n\n[Contexto visual capturado de la ventana activa: '{window_title}']\n"
                        "Texto detectado en pantalla mediante reconocimiento óptico de caracteres (OCR):\n"
                        f"\"\"\"\n{content}\n\"\"\"\n"
                    )
                    self.record_system_action(f"Lectura de pantalla ({window_title})", f"Texto extraído por OCR: {len(content)} caracteres")
                elif mode == "image":
                    temp_visual_file = content
                    screen_context = (
                        f"\n\n[Contexto visual capturado de la ventana activa: '{window_title}']\n"
                        "El texto extraído por OCR fue insuficiente o se solicitó análisis visual/gráfico explícito.\n"
                        f"Se tomó una captura temporal guardada en: '{temp_visual_file}'.\n"
                        "Por favor analiza la imagen usando visión multimodal para responder a la consulta del usuario.\n"
                    )
                    self.record_system_action(f"Captura para análisis ({window_title})", f"Captura temporal enviada para visión multimodal: {temp_visual_file}")

        full_prompt = f"{voice_context}{screen_context}{prompt}"

        memory_mode = getattr(config, "SESSION_MEMORY_MODE", "per_session")
        project_id = getattr(config, "AGY_PROJECT_ID", "asistente-voz")
        print_timeout = getattr(config, "AGY_PRINT_TIMEOUT", "20m")

        flags = []
        if project_id:
            flags.extend(["--project", project_id])

        if print_timeout:
            flags.extend(["--print-timeout", str(print_timeout)])

        if memory_mode == "per_session":
            if self.has_active_conversation:
                flags.append("-c")
        elif memory_mode == "persistent":
            flags.append("-c")

        flags.extend(["-p", full_prompt])
        cmd = [self.agy_cmd] + flags

        try:
            with console.status("[bold cyan]🤖 Antigravity pensando y ejecutando...[/bold cyan]", spinner="dots"):
                try:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=self.working_directory,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace"
                    )
                    output, _ = proc.communicate()
                except Exception as e:
                    console.print(f"[bold red]❌ Error al ejecutar Antigravity CLI:[/bold red] {e}")
                    sound_effects.play_error()
                    return
        finally:
            if temp_visual_file and os.path.exists(temp_visual_file):
                try:
                    os.remove(temp_visual_file)
                except Exception:
                    pass

        if proc.returncode == 0:
            self.has_active_conversation = True

        sound_effects.play_success()

        output_text = output.strip() if output else "Comando completado sin salida."

        action_matches = re.findall(r'\[ACTION:\s*(OPEN_URL|OPEN_APP|SCREENSHOT)\s*([^\]]*)\]', output_text, re.IGNORECASE)
        for action_type, action_target in action_matches:
            target = action_target.strip().strip('"\'')
            act_upper = action_type.upper()
            if act_upper == "OPEN_URL":
                open_url_native(target)
            elif act_upper == "OPEN_APP":
                try:
                    subprocess.Popen(target, shell=True)
                except Exception as err:
                    console.print(f"[red]Error al abrir aplicación {target}:[/red] {err}")
            elif act_upper == "SCREENSHOT":
                saved_path = take_screenshot()
                if saved_path:
                    console.print(f"[bold green]📸 Captura guardada en:[/bold green] {saved_path}")
                    self.record_system_action("Captura de pantalla", f"Captura guardada en: {saved_path}")

        clean_text = re.sub(r'\[ACTION:\s*(?:OPEN_URL|OPEN_APP|SCREENSHOT)\s*[^\]]*\]', '', output_text).strip()
        display_text = clean_text if clean_text else "Acción completada."

        panel = Panel(
            Markdown(display_text),
            title=f"[bold cyan]🤖 Antigravity CLI[/bold cyan] [dim]({os.path.basename(self.working_directory)})[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        import importlib
        importlib.reload(config)
        should_speak = getattr(config, "TTS_ENABLED", True) and bool(clean_text)
        if action_matches and len(clean_text) < 180:
            should_speak = False

        if should_speak:
            with console.status("[bold magenta]🔊 Hablando...[/bold magenta]", spinner="point"):
                self.speaker.speak(clean_text)
