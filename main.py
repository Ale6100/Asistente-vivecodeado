"""
=============================================================
ANTIGRAVITY VOICE ASSISTANT (Control por Voz y Texto para 'agy')
=============================================================
"""
import sys
import os
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import threading
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from pynput import keyboard

try:
    import msvcrt
    MSVCRT_AVAILABLE = True
except ImportError:
    MSVCRT_AVAILABLE = False

import config
import sound_effects
from audio_engine import AudioEngine
from transcriber import WhisperTranscriber
from cli_launcher import AgyLauncher
from system_controller import SystemController

console = Console()

manual_trigger_event = threading.Event()

def format_hotkey(hotkey: str | None) -> str:
    if not hotkey:
        return ""
    h = hotkey.strip().lower()
    if not h.startswith("<") and not "+" in h:
        return f"<{h}>"
    return h

def setup_hotkey_listener(get_launcher_cb):
    ptt_raw = getattr(config, "HOTKEY_PUSH_TO_TALK", "f8")
    interrupt_raw = getattr(config, "HOTKEY_INTERRUPT", None)

    formatted_ptt = format_hotkey(ptt_raw)
    formatted_interrupt = format_hotkey(interrupt_raw) if interrupt_raw else None

    def on_interrupt():
        launcher = get_launcher_cb()
        if launcher is not None:
            was_busy = launcher.interrupt()
            if was_busy:
                sound_effects.play_interrupted()
                console.print("\n[bold yellow]⏹️ Asistente interrumpido explícitamente.[/bold yellow]")

    def on_ptt():
        launcher = get_launcher_cb()
        if launcher is not None and (launcher.is_busy or launcher.speaker.is_speaking):
            on_interrupt()
        else:
            manual_trigger_event.set()

    hotkey_map = {}
    if formatted_ptt:
        hotkey_map[formatted_ptt] = on_ptt
    if formatted_interrupt and formatted_interrupt != formatted_ptt:
        hotkey_map[formatted_interrupt] = on_interrupt

    try:
        hotkeys = keyboard.GlobalHotKeys(hotkey_map)
        hotkeys.start()
        return hotkeys, formatted_ptt, formatted_interrupt
    except Exception:
        try:
            if formatted_ptt:
                hotkeys = keyboard.GlobalHotKeys({formatted_ptt: on_ptt})
                hotkeys.start()
                return hotkeys, formatted_ptt, formatted_interrupt
            return None, formatted_ptt, formatted_interrupt
        except Exception:
            return None, formatted_ptt, formatted_interrupt

def print_banner(formatted_ptt: str, formatted_interrupt: str | None, mic_name: str, working_dir: str, model_name: str, reasoning_effort: str):
    wake_display = ", ".join([w.replace("_", " ").title() for w in config.WAKE_WORDS])
    tts_status = f"Activada ({config.TTS_RATE})" if getattr(config, "TTS_ENABLED", True) else "Desactivada"
    memory_mode = getattr(config, "SESSION_MEMORY_MODE", "per_session")
    memory_display = "Por Sesión (Limpia al iniciar)" if memory_mode == "per_session" else ("Persistente" if memory_mode == "persistent" else "Sin memoria")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("🤖 [bold cyan]Modelo de lenguaje:[/bold cyan]", f"[bold magenta]{model_name}[/bold magenta]")
    table.add_row("⚡ [bold cyan]Nivel de razonamiento:[/bold cyan]", f"[bold magenta]{reasoning_effort}[/bold magenta]")
    table.add_row("📁 [bold cyan]Repositorio / Carpeta activa:[/bold cyan]", f"[bold yellow]{working_dir}[/bold yellow]")
    table.add_row("🧠 [bold cyan]Memoria de conversación:[/bold cyan]", f"[bold green]{memory_display}[/bold green]")
    table.add_row("🗣️ [bold cyan]Palabra de activación:[/bold cyan]", f"[bold green]{wake_display}[/bold green]")
    table.add_row("⌨️ [bold cyan]Atajo de voz (Toggle):[/bold cyan]", f"[bold green]{formatted_ptt}[/bold green]")
    if formatted_interrupt and formatted_interrupt != formatted_ptt:
        table.add_row("⏹️ [bold cyan]Atajo de interrupción rápida:[/bold cyan]", f"[bold yellow]{formatted_interrupt}[/bold yellow] o pulsar [bold yellow]{formatted_ptt}[/bold yellow]")
    else:
        table.add_row("⏹️ [bold cyan]Atajo de interrupción rápida:[/bold cyan]", f"Pulsar [bold yellow]{formatted_ptt}[/bold yellow]")
    table.add_row("📝 [bold cyan]Modo escritura por teclado:[/bold cyan]", "[bold yellow]Pulsa [Enter] o [T][/bold yellow]")
    table.add_row("🔊 [bold cyan]Respuesta por voz (TTS):[/bold cyan]", f"[bold green]{tts_status}[/bold green]")
    table.add_row("🎙️ [bold cyan]Micrófono:[/bold cyan]", f"[white]{mic_name}[/white]")

    panel = Panel(
        table,
        title="[bold blue]🤖 ANTIGRAVITY VOICE & TEXT ASSISTANT[/bold blue]",
        subtitle="[dim]Presiona Ctrl+C para salir[/dim]",
        border_style="bright_blue"
    )
    console.print(panel)


def try_handle_session_reset(text: str, launcher: AgyLauncher) -> bool:
    clean = text.strip().lower()
    reset_triggers = (
        "/reset", "/new", "/clear", "/nueva",
        "nueva sesión", "nueva sesion", "nueva conversación", "nueva conversacion",
        "reiniciar sesión", "reiniciar sesion", "reiniciar memoria", "reiniciar conversación",
        "reiniciar conversacion", "olvidar conversación", "olvidar conversacion", "olvida lo anterior",
        "olvidá lo anterior", "olvida todo", "olvidá todo", "empezar de cero", "limpiar contexto", "limpiar memoria"
    )
    if clean in reset_triggers:
        launcher.reset_conversation()
        msg = "Sesión reiniciada. Empezamos una conversación limpia."
        panel = Panel(
            Markdown(msg),
            title="[bold cyan]🔄 Memoria Reiniciada[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        console.print(panel)
        sound_effects.play_success()
        return True
    return False

def try_handle_directory_change(text: str, launcher: AgyLauncher) -> tuple[bool, bool]:
    clean = text.strip()
    clean_lower = clean.lower()
    prefixes = ("/cd ", "cd ", "/c ", "c ", "/dir ", "/folder ")
    path = None
    if clean_lower.startswith(prefixes):
        _, path = clean.split(" ", 1)
    else:
        match = re.match(r'^(?:cambiar\s+(?:de\s+)?(?:carpeta|directorio|proyecto)(?:\s+a)?|carpeta|directorio)\s+(.+)$', clean, re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if os.path.exists(candidate.strip("\"' ")):
                path = candidate

    if path is not None:
        ok, msg = launcher.set_working_directory(path)
        if ok:
            launcher.record_system_action(clean, f"Carpeta cambiada a {launcher.working_directory}")
            console.print(f"[bold green]📁 Carpeta cambiada a:[/bold green] {launcher.working_directory}")
            sound_effects.play_success()
        else:
            console.print(f"[bold red]❌ Error:[/bold red] {msg}")
            sound_effects.play_error()
        return True, ok
    return False, False

def process_instruction(prompt: str, launcher: AgyLauncher, system_controller: SystemController) -> bool:
    if try_handle_session_reset(prompt, launcher):
        return True

    handled_dir, _ = try_handle_directory_change(prompt, launcher)
    if handled_dir:
        return True

    handled, message, should_exit, speak_response = system_controller.handle_command(prompt)
    if should_exit:
        console.print(f"\n[bold red]🛑 {message}[/bold red]")
        if getattr(config, "TTS_ENABLED", True) and speak_response:
            launcher.speaker.speak(message)
        return False

    if handled:
        launcher.record_system_action(prompt, message)
        panel = Panel(
            Markdown(message),
            title="[bold green]⚡ Acción del Sistema[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        console.print(panel)
        sound_effects.play_success()
        if getattr(config, "TTS_ENABLED", True) and speak_response:
            launcher.speaker.speak(message)
        return True

    launcher.execute_prompt(prompt)
    return True

def handle_text_mode(launcher: AgyLauncher, audio_engine: AudioEngine, system_controller: SystemController) -> bool:
    """
    Pausa el micrófono temporalmente para permitir escribir una orden por teclado
    o cambiar de repositorio con '/cd <ruta>'.
    """
    audio_engine.pause()
    console.print("\n[bold cyan]⌨️ Modo Escritura activado.[/bold cyan]")
    console.print("[dim]Escribe tu orden para Antigravity, '/cd <ruta>' para cambiar de proyecto, o '/new' para reiniciar memoria (Enter vacío para cancelar):[/dim]")

    try:
        user_input = input("👉 ").strip()
    except Exception:
        user_input = ""

    continue_running = True
    if user_input:
        handled_dir, _ = try_handle_directory_change(user_input, launcher)
        if not handled_dir:
            continue_running = process_instruction(user_input, launcher, system_controller)

    audio_engine.start()
    console.print("\n[bold green]🟢 Listo.[/bold green] Esperando comando por voz o pulsa [Enter] para escribir...\n")
    return continue_running

def main():
    launcher_ref = [None]
    hotkey_listener, formatted_ptt, formatted_interrupt = setup_hotkey_listener(lambda: launcher_ref[0])

    try:
        with console.status("[bold cyan]Iniciando servicios del asistente...", spinner="dots") as status:
            status.update("[bold cyan]Inicializando motor de audio y micrófono...")
            audio_engine = AudioEngine()

            status.update("[bold cyan]Cargando modelo de transcripción Whisper...")
            transcriber = WhisperTranscriber()

            status.update("[bold cyan]Conectando con Antigravity y entorno...")
            launcher = AgyLauncher()
            launcher_ref[0] = launcher
            system_controller = SystemController(speaker=launcher.speaker)
    except Exception as e:
        console.print(f"[bold red]❌ Error al inicializar:[/bold red] {e}")
        return

    model_name, reasoning_effort = launcher.get_model_info()
    print_banner(formatted_ptt, formatted_interrupt, audio_engine.device_name, launcher.working_directory, model_name, reasoning_effort)
    wake_display = config.WAKE_WORDS[0].replace("_", " ").title()
    console.print(f"\n[bold green]🟢 Listo.[/bold green] Di '[bold cyan]{wake_display}[/bold cyan]', presiona '[bold cyan]{formatted_ptt}[/bold cyan]', o pulsa '[bold cyan]Enter[/bold cyan]' para escribir.")
    if formatted_interrupt and formatted_interrupt != formatted_ptt:
        console.print(f"[dim]Tip: Puedes interrumpir al asistente en cualquier momento pulsando '{formatted_interrupt}' o '{formatted_ptt}'.[/dim]\n")
    else:
        console.print(f"[dim]Tip: Puedes interrumpir al asistente en cualquier momento pulsando '{formatted_ptt}'.[/dim]\n")

    audio_engine.start()


    try:
        while True:
            # 1. Modo teclado (Enter o T)
            if MSVCRT_AVAILABLE and msvcrt.kbhit():
                key = msvcrt.getwch()
                if key in ('\r', '\n', 't', 'T'):
                    keep_going = handle_text_mode(launcher, audio_engine, system_controller)
                    if not keep_going:
                        break
                    continue

            # 2. Modo voz
            is_wake_word = audio_engine.check_wake_word()
            is_manual_key = manual_trigger_event.is_set()

            if is_wake_word or is_manual_key:
                manual_trigger_event.clear()

                audio_data = audio_engine.record_user_instruction(stop_event=manual_trigger_event)

                if audio_data is not None and len(audio_data) > 0:
                    with console.status("[bold yellow]Procesando...[/bold yellow]", spinner="dots"):
                        raw_prompt = transcriber.transcribe(audio_data)
                        clean_prompt, is_valid, reason = transcriber.clean_and_validate(raw_prompt)

                    if is_valid:
                        console.print(f"[bold green]📝 Instrucción:[/bold green] \"{clean_prompt}\"")
                        audio_engine.pause()
                        keep_going = process_instruction(clean_prompt, launcher, system_controller)
                        audio_engine.start()
                        if not keep_going:
                            break
                    else:
                        console.print(f"[yellow]⚠️ {reason}. Descartado.[/yellow]")
                        sound_effects.play_error()
                else:
                    console.print("[dim]Grabación descartada o vacía.[/dim]")

                console.print("\n[bold green]🟢 Listo.[/bold green] Esperando comando...\n")

    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Deteniendo asistente... Hasta luego.[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {e}")
    finally:
        audio_engine.close()
        if hotkey_listener is not None:
            hotkey_listener.stop()

if __name__ == "__main__":
    main()
