import os
import re
import time
import base64
import ctypes
import subprocess
from datetime import datetime

import config

user32 = ctypes.windll.user32

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

OCR_MIN_CHARS_THRESHOLD = getattr(config, "SCREEN_OCR_MIN_CHARS", 30)

SCREEN_INSPECTION_PATTERN = re.compile(
    r'(?:'
    r'mir[aá]\s+(?:la\s+pantalla|mi\s+pantalla|esta\s+pantalla|la\s+ventana|la\s+consola|la\s+terminal|esto|ac[aá])|'
    r'f[ií]jate\s+(?:en\s+)?(?:la\s+pantalla|mi\s+pantalla|la\s+ventana|la\s+consola|la\s+terminal|esto|este\s+error)|'
    r'qu[eé]\s+(?:hay|dice|ves|pasa|ocurre|fall[oó]|sali[oó]\s+mal)\s+(?:en\s+)?(?:la\s+pantalla|la\s+terminal|la\s+consola|la\s+ventana)|'
    r'analiz[aá]\s+(?:la\s+pantalla|la\s+ventana|lo\s+que\s+tengo|lo\s+que\s+estoy\s+viendo|este\s+error|este\s+gr[aá]fico|esta\s+interfaz|esto)|'
    r'le[eé]\s+(?:la\s+pantalla|la\s+consola|la\s+terminal|lo\s+que\s+hay\s+en\s+pantalla|lo\s+que\s+dice\s+la\s+pantalla)|'
    r'revis[aá]\s+(?:la\s+pantalla|mi\s+pantalla|la\s+consola|la\s+terminal|este\s+error)|'
    r'por\s+qu[eé]\s+(?:falla|fall[oó]|da\s+error)\s+(?:esto|mi\s+c[oó]digo|la\s+terminal)|'
    r'explicame\s+(?:este\s+error|lo\s+que\s+(?:estoy\s+viendo|hay\s+en\s+pantalla))|'
    r'expl[ií]came\s+(?:este\s+error|lo\s+que\s+(?:estoy\s+viendo|hay\s+en\s+pantalla))|'
    r'(?:pantalla|ventana|consola|terminal)\s+(?:y\s+decime|y\s+decirme|y\s+explicame)|'
    r'(?:cu[aá]l\s+es\s+tu\s+opini[oó]n|dame\s+tu\s+opini[oó]n|qu[eé]\s+(?:opin[aá]s|pens[aá]s|te\s+parece)|c[oó]mo\s+(?:lo\s+)?ves|opin[aá])\s+(?:de\s+|sobre\s+|acerca\s+de\s+)?(?:esto|ac[aá]|la\s+pantalla|esta\s+ventana|esta\s+pantalla|lo\s+que\s+(?:hay|ves|estoy\s+viendo))'
    r')',
    re.IGNORECASE
)

VISUAL_KEYWORDS_PATTERN = re.compile(
    r'\b(?:gr[aá]fico|gr[aá]fica|diseño|diseno|dibujo|imagen|foto|colores|color|est[eé]tica|maqueta|diagrama|interfaz|ui|layout|posici[oó]n|posicion|alineaci[oó]n|alineacion|visual|visualmente)\b',
    re.IGNORECASE
)

FULLSCREEN_KEYWORDS_PATTERN = re.compile(
    r'\b(?:toda\s+la\s+pantalla|pantalla\s+completa|todo\s+el\s+escritorio|todo\s+el\s+monitor)\b',
    re.IGNORECASE
)

def is_screen_inspection_request(prompt: str) -> bool:
    if not prompt:
        return False
    return bool(SCREEN_INSPECTION_PATTERN.search(prompt))

def is_visual_analysis_request(prompt: str) -> bool:
    if not prompt:
        return False
    return bool(VISUAL_KEYWORDS_PATTERN.search(prompt))

def should_capture_fullscreen(prompt: str) -> bool:
    if not prompt:
        return False
    return bool(FULLSCREEN_KEYWORDS_PATTERN.search(prompt))

def get_active_window_info() -> tuple[str, dict]:
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "Pantalla Principal", {}

    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    title = buff.value.strip()

    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width < 50 or height < 50:
        return "Pantalla Principal", {}

    window_rect = {
        "left": rect.left,
        "top": rect.top,
        "width": width,
        "height": height
    }
    display_title = title if title else "Ventana Activa"
    return display_title, window_rect

def execute_in_memory_ocr(window_rect: dict | None = None) -> str:
    rect_arg = ""
    if window_rect and window_rect.get("width", 0) > 0 and window_rect.get("height", 0) > 0:
        rect_arg = f"$x = {window_rect['left']}; $y = {window_rect['top']}; $w = {window_rect['width']}; $h = {window_rect['height']};"
    else:
        rect_arg = "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $x = $b.X; $y = $b.Y; $w = $b.Width; $h = $b.Height;"

    ps_code = f"""
Add-Type -AssemblyName System.Runtime.WindowsRuntime
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation.UniversalApiContract, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null

{rect_arg}

$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
$g.Dispose()

$ms = New-Object System.IO.MemoryStream
$bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
$bytes = $ms.ToArray()
$bmp.Dispose()
$ms.Dispose()

$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.IsGenericMethod }})[0]

function Await-Op($op, $type) {{
    $m = $asTask.MakeGenericMethod($type)
    $t = $m.Invoke($null, @($op))
    return $t.GetAwaiter().GetResult()
}}

$ras = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
$dw = New-Object Windows.Storage.Streams.DataWriter $ras
$dw.WriteBytes($bytes)
$null = Await-Op ($dw.StoreAsync()) ([System.UInt32])
$null = Await-Op ($dw.FlushAsync()) ([System.Boolean])
$dw.DetachStream() | Out-Null
$dw.Dispose()
$ras.Seek(0)

$decoder = Await-Op ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($ras)) ([Windows.Graphics.Imaging.BitmapDecoder])
$sbm = Await-Op ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $engine) {{
    $langs = [Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages
    if ($langs.Count -gt 0) {{
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($langs[0])
    }}
}}

if ($engine) {{
    $ocrResult = Await-Op ($engine.RecognizeAsync($sbm)) ([Windows.Media.Ocr.OcrResult])
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Host $ocrResult.Text
}}
$ras.Dispose()
"""
    try:
        b64 = base64.b64encode(ps_code.encode("utf-16le")).decode("ascii")
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-EncodedCommand", b64],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return proc.stdout.strip()
    except Exception:
        return ""

def capture_window_to_file(window_rect: dict | None = None, target_path: str = "") -> str:
    if not target_path:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, "screenshots")
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = os.path.join(folder, f"temp_inspect_{timestamp}.png")

    rect_arg = ""
    if window_rect and window_rect.get("width", 0) > 0 and window_rect.get("height", 0) > 0:
        rect_arg = f"$x = {window_rect['left']}; $y = {window_rect['top']}; $w = {window_rect['width']}; $h = {window_rect['height']};"
    else:
        rect_arg = "$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; $x = $b.X; $y = $b.Y; $w = $b.Width; $h = $b.Height;"

    normalized_path = target_path.replace("\\", "/")
    ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms,System.Drawing
{rect_arg}
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($x, $y, 0, 0, (New-Object System.Drawing.Size $w, $h))
$bmp.Save('{normalized_path}')
$g.Dispose()
$bmp.Dispose()
"""
    try:
        b64 = base64.b64encode(ps_code.encode("utf-16le")).decode("ascii")
        subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", b64], capture_output=True, check=True)
        if os.path.exists(target_path):
            return target_path
    except Exception:
        pass
    return ""

def inspect_screen_for_prompt(prompt: str) -> tuple[str, str, str]:
    fullscreen = should_capture_fullscreen(prompt)
    if fullscreen:
        title = "Toda la Pantalla"
        rect = None
    else:
        title, rect = get_active_window_info()

    explicit_visual = is_visual_analysis_request(prompt)
    ocr_text = execute_in_memory_ocr(rect)

    has_enough_text = len(ocr_text.strip()) >= OCR_MIN_CHARS_THRESHOLD

    if has_enough_text and not explicit_visual:
        return "ocr", ocr_text, title

    image_path = capture_window_to_file(rect)
    return "image", image_path, title
