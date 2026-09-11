import sys
import os
import shutil
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
import sound_effects
from tts_speaker import TTSSpeaker

console = Console()

class AgyLauncher:
    def __init__(self):
        self.agy_cmd = config.AGY_COMMAND
        self.speaker = TTSSpeaker()

        if config.DEFAULT_PROJECT_DIR and os.path.isdir(config.DEFAULT_PROJECT_DIR):
            self.working_directory = os.path.abspath(config.DEFAULT_PROJECT_DIR)
        else:
            self.working_directory = os.getcwd()

        if not shutil.which(self.agy_cmd):
            console.print(f"[yellow]⚠️ Advertencia: No se encontró '{self.agy_cmd}' en el PATH del sistema.[/yellow]")

    def set_working_directory(self, new_dir: str) -> tuple[bool, str]:
        clean_path = new_dir.strip().strip('"').strip("'")
        expanded = os.path.abspath(os.path.expanduser(clean_path))
        if os.path.isdir(expanded):
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

        voice_context = (
            "[CONSIGNA DE CONTEXTO DEL SISTEMA]: "
            "El usuario se está comunicando contigo mediante voz y micrófono como su asistente virtual. "
            f"Carpeta de trabajo actual: '{self.working_directory}'. "
            "Tu respuesta será sintetizada en audio (TTS) para que el usuario la escuche. "
            "Directrices esenciales: "
            "1. Sé directo, conversacional y conciso (máximo 2 a 3 frases). "
            "2. Para desarrollo: ejecuta las acciones reales (crear/editar archivos, git, comandos) en la carpeta de trabajo y resume lo que hiciste. "
            "3. Para control de la PC (abrir páginas web, aplicaciones, música, consultar el sistema): EJECUTA los comandos reales del sistema operativo (ej: en PowerShell `Start-Process 'https://...'` o el ejecutable del programa). NUNCA digas que hiciste algo o que abriste algo si no ejecutaste el comando real mediante tus herramientas de terminal. "
            "4. No incluyas bloques largos de código en el texto de tu respuesta para que la lectura por voz sea fluida. "
            "\n\nInstrucción del usuario:\n"
        )

        full_prompt = f"{voice_context}{prompt}"

        flags = ["-p", full_prompt]
        if config.CONTINUE_PREVIOUS_CONVERSATION:
            flags = ["-c", "-p", full_prompt]

        cmd = [self.agy_cmd] + flags

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

        sound_effects.play_success()

        output_text = output.strip() if output else "Comando completado sin salida."

        panel = Panel(
            Markdown(output_text),
            title=f"[bold cyan]🤖 Antigravity CLI[/bold cyan] [dim]({os.path.basename(self.working_directory)})[/dim]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)

        import importlib
        importlib.reload(config)
        if getattr(config, "TTS_ENABLED", True):
            with console.status("[bold magenta]🔊 Hablando...[/bold magenta]", spinner="point"):
                self.speaker.speak(output_text)
