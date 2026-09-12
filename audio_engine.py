"""
Motor de Audio Robusto con Auto-Detección de Micrófono, Resampling, Ganancia Automática y Wake-Word.
"""
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import time
import queue
import logging
import warnings
import numpy as np
import scipy.signal as signal
import sounddevice as sd
from rich.console import Console
from openwakeword.model import Model

import config
import sound_effects

console = Console()

warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)

TARGET_SAMPLE_RATE = 16000
TARGET_CHUNK_SIZE = 1280

def find_best_microphone():
    """
    Detecta automáticamente el micrófono funcional con mejor señal en Windows.
    Prueba primero el dispositivo configurado/predeterminado, y si falla por
    errores de host (MME error 1 o DirectSound), prueba dispositivos WDM-KS/WASAPI.
    """
    def _test_device(idx, sr):
        captured = []
        def _cb(indata, frames, time_info, status):
            captured.append(indata.copy())
        try:
            block = int(sr * 0.08)
            with sd.InputStream(device=idx, samplerate=sr, blocksize=block, channels=1, callback=_cb):
                time.sleep(0.12)
            arr = np.concatenate(captured, axis=0) if captured else np.zeros(1)
            rms = float(np.sqrt(np.mean(arr**2)))
            return True, rms
        except Exception:
            return False, 0.0

    if config.INPUT_DEVICE_INDEX is not None:
        for sr in [16000, 48000, 44100]:
            ok, rms = _test_device(config.INPUT_DEVICE_INDEX, sr)
            if ok:
                dev_info = sd.query_devices(config.INPUT_DEVICE_INDEX)
                return config.INPUT_DEVICE_INDEX, sr, dev_info['name']

    for sr in [16000, 48000, 44100]:
        ok, rms = _test_device(None, sr)
        if ok:
            return None, sr, "Micrófono Predeterminado de Windows"

    devices = sd.query_devices()
    candidates = []
    for idx, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            name = d['name'].lower()
            if 'mezcla' in name or 'stereo mix' in name or 'steam' in name:
                continue
            for sr in [48000, 16000, 44100]:
                ok, rms = _test_device(idx, sr)
                if ok:
                    candidates.append((rms, idx, sr, d['name']))
                    break

    if candidates:
        candidates.sort(reverse=True)
        best_rms, best_idx, best_sr, best_name = candidates[0]
        return best_idx, best_sr, best_name

    return None, 16000, "Dispositivo predeterminado (Fallback)"


class AudioEngine:
    def __init__(self):
        print("🔍 Detectando micrófono en el sistema...")
        self.device_idx, self.native_sr, self.device_name = find_best_microphone()
        print(f"🎙️ Micrófono seleccionado: [ID {self.device_idx}] {self.device_name} ({self.native_sr} Hz)")

        self.native_block_size = int(self.native_sr * 0.08)
        self.audio_queue = queue.Queue(maxsize=200)
        self.ambient_rms = 0.0003
        self.is_running = False

        print("🧠 Cargando modelo openWakeWord...")
        try:
            self.wakeword_model = Model(
                wakeword_models=list(config.WAKE_WORDS),
                inference_framework="onnx"
            )
        except Exception:
            import openwakeword.utils
            print("📥 Descargando modelos de activación necesarios...")
            openwakeword.utils.download_models(list(config.WAKE_WORDS))
            self.wakeword_model = Model(
                wakeword_models=list(config.WAKE_WORDS),
                inference_framework="onnx"
            )
        print(f"✅ Palabra(s) de activación listas.")

        self._create_stream()

    def _create_stream(self):
        """Inicializa el stream de captura de PortAudio."""
        self.stream = sd.InputStream(
            device=self.device_idx,
            samplerate=self.native_sr,
            blocksize=self.native_block_size,
            channels=1,
            callback=self._audio_callback
        )

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback llamado continuamente por el hardware de audio."""
        if not self.is_running:
            return

        raw_channel = indata[:, 0].astype(np.float32)

        if self.native_sr == 16000:
            resampled = raw_channel
        elif self.native_sr == 48000:
            resampled = signal.resample_poly(raw_channel, 1, 3)
        elif self.native_sr == 44100:
            resampled = signal.resample_poly(raw_channel, 160, 441)
        else:
            target_len = int(len(raw_channel) * (TARGET_SAMPLE_RATE / self.native_sr))
            resampled = signal.resample(raw_channel, target_len)

        if len(resampled) > TARGET_CHUNK_SIZE:
            resampled = resampled[:TARGET_CHUNK_SIZE]
        elif len(resampled) < TARGET_CHUNK_SIZE:
            resampled = np.pad(resampled, (0, TARGET_CHUNK_SIZE - len(resampled)))

        chunk_rms = float(np.sqrt(np.mean(resampled ** 2)))
        self.ambient_rms = 0.97 * self.ambient_rms + 0.03 * chunk_rms

        int16_frame = (resampled * 32767.0).clip(-32768, 32767).astype(np.int16)
        float32_frame = resampled.astype(np.float32)

        try:
            self.audio_queue.put_nowait((int16_frame, float32_frame))
        except queue.Full:
            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait((int16_frame, float32_frame))
            except Exception:
                pass

    def start(self):
        """Inicia o reanuda la captura continua de audio."""
        if not self.is_running:
            self.is_running = True
            try:
                if getattr(self.stream, 'closed', False):
                    self._create_stream()
                self.stream.start()
            except Exception:
                self._create_stream()
                self.stream.start()

    def pause(self):
        """Pausa temporalmente la captura sin destruir el stream."""
        if self.is_running:
            self.is_running = False
            try:
                self.stream.stop()
            except Exception:
                pass
            self.clear_queue()

    def stop(self):
        """Alias para pause."""
        self.pause()

    def close(self):
        """Cierra definitivamente el stream al salir del programa."""
        self.is_running = False
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass

    def check_wake_word(self) -> bool:
        """Lee el siguiente bloque de la cola y evalúa si coincide con la palabra de activación."""
        try:
            int16_frame, _ = self.audio_queue.get(timeout=0.1)
        except queue.Empty:
            return False

        predictions = self.wakeword_model.predict(int16_frame)

        for wake_word in config.WAKE_WORDS:
            score = predictions.get(wake_word, 0.0)
            if score >= config.WAKE_WORD_THRESHOLD:
                self.wakeword_model.reset()
                return True

        return False

    def clear_queue(self):
        """Vacía los frames antiguos acumulados en la cola."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def record_user_instruction(self, stop_event=None) -> np.ndarray:
        """
        Graba la instrucción del usuario permitiendo pausas naturales para pensar.
        """
        sound_effects.play_wake_detected()
        console.print("\n🎤 [bold red]🔴 Escuchando...[/bold red]")

        self.clear_queue()

        recorded_chunks = []
        has_detected_speech = False
        silence_start_time = None
        start_time = time.time()

        speech_threshold = max(self.ambient_rms * 1.8, config.SILENCE_THRESHOLD)

        while True:
            if stop_event is not None and stop_event.is_set():
                stop_event.clear()
                break

            try:
                _, float32_frame = self.audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            recorded_chunks.append(float32_frame)

            rms = float(np.sqrt(np.mean(float32_frame ** 2)))
            current_time = time.time()
            elapsed_time = current_time - start_time

            if rms > speech_threshold:
                has_detected_speech = True
                silence_start_time = None
            else:
                if has_detected_speech:
                    if silence_start_time is None:
                        silence_start_time = current_time
                    elif (current_time - silence_start_time) >= config.SILENCE_DURATION:
                        if elapsed_time >= config.MIN_RECORD_SECONDS:
                            break

            if elapsed_time >= config.MAX_RECORD_SECONDS:
                break

        sound_effects.play_recording_stop()

        if not recorded_chunks:
            return None

        full_audio = np.concatenate(recorded_chunks, axis=0)
        duration = len(full_audio) / TARGET_SAMPLE_RATE

        if duration < 0.5:
            return None

        peak = float(np.max(np.abs(full_audio)))
        if peak > 0.0001:
            full_audio = (full_audio / peak) * 0.9

        return full_audio
