import subprocess
import shutil
import json
import os
import re
import webbrowser
import urllib.parse
import unicodedata
import sys
import time
import psutil
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pyautogui

INDEX_PATH = os.path.join(os.path.dirname(__file__), "programas_index.json")

RUTAS_BASE = [
    "C:\\Program Files",
    "C:\\Program Files (x86)"
]

ALIAS = {
    "word": "winword",
    "powerpoint": "powerpnt",
    "excel": "excel",
    "outlook": "outlook",
    "reloj": "Microsoft.WindowsAlarms_8wekyb3d8bbwe!App",
    "calculadora": "Microsoft.WindowsCalculator_8wekyb3d8bbwe!App",
    "fotos": "Microsoft.Windows.Photos_8wekyb3d8bbwe!App",
    "configuración": "windows.immersivecontrolpanel",
    "tienda": "Microsoft.WindowsStore_8wekyb3d8bbwe!App",
    "notas": "Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe!App",
}

def limpiar_nombre(nombre):
    nombre = nombre.lower().strip()
    nombre = re.sub(r"\b(el|la|los|las|un|una|unos|unas)\b", "", nombre)
    nombre = re.sub(r"\s+", " ", nombre).strip()
    return nombre

def generar_indice():
    index = {}
    for base in RUTAS_BASE:
        if os.path.exists(base):
            for root, dirs, files in os.walk(base):
                for file in files:
                    if file.lower().endswith(".exe"):
                        nombre = file.lower().replace(".exe", "").strip()
                        if nombre not in index:
                            index[nombre] = os.path.join(root, file)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Índice generado con {len(index)} programas en {INDEX_PATH}")

def abrir_app(nombre_app, apps_dict):
    nombre_app = limpiar_nombre(nombre_app)
    for alias, destino in ALIAS.items():
        if alias in nombre_app:
            if "!" in destino:
                subprocess.Popen(["explorer", f"shell:appsFolder\\{destino}"])
                print(f"Abriendo app de Microsoft Store: {alias}")
                return
            elif destino == "windows.immersivecontrolpanel":
                subprocess.Popen(["start", "ms-settings:"], shell=True)
                print("Abriendo Configuración de Windows")
                return
            else:
                if shutil.which(destino):
                    subprocess.Popen([destino])
                    print(f"Abriendo {destino} (alias directo)...")
                    return
                else:
                    print(f"No está en PATH, buscando en índice con alias '{destino}'...")
                    abrir_desde_indice(destino)
                    return
    comando = apps_dict.get(nombre_app, None)
    if comando:
        if shutil.which(comando):
            subprocess.Popen([comando])
            print(f"Abriendo {comando} (diccionario)...")
            return
        else:
            print(f"No está en PATH, buscando en índice...")
    abrir_desde_indice(nombre_app)

def abrir_desde_indice(nombre):
    if not os.path.exists(INDEX_PATH):
        generar_indice()
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    nombre = nombre.lower().strip()
    if nombre in index:
        return ejecutar_programa(index[nombre])
    for clave, ruta in index.items():
        if nombre in clave:
            return ejecutar_programa(ruta)
    print(f"No se encontró un programa que coincida con '{nombre}' en el índice.")

def ejecutar_programa(ruta):
    try:
        if "WindowsApps" in ruta:
            app_id = detectar_app_id(ruta)
            if app_id:
                subprocess.Popen(["explorer", f"shell:appsFolder\\{app_id}"])
                print(f"Abriendo app de Microsoft Store: {app_id}")
                return
        subprocess.Popen([ruta])
        print(f"Abriendo desde índice: {ruta}")
    except Exception as e:
        print(f"Error al abrir {ruta}: {e}")

def detectar_app_id(ruta):
    try:
        carpeta = os.path.basename(os.path.dirname(ruta))
        nombre = carpeta.split("_")[0]
        exe_name = os.path.splitext(os.path.basename(ruta))[0]
        if "__" in carpeta:
            sufijo = carpeta.split("__")[1]
            return f"{nombre}_{sufijo}!{exe_name}"
    except:
        pass
    return None

def set_volume(percent):
    percent = max(0, min(percent, 100))
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    min_vol, max_vol, _ = volume.GetVolumeRange()
    volume_level = min_vol + (max_vol - min_vol) * (percent / 100.0)
    volume.SetMasterVolumeLevel(volume_level, None)
    print(f"Volumen ajustado a {percent}%")

def procesar_busqueda(arg, motor=None):
    if motor is None:
        orden = str(arg).lower().strip()
        if orden.startswith("busca en google"):
            consulta = orden.replace("busca en google", "").strip()
            motor = "google"
        elif orden.startswith("busca en chatgpt"):
            consulta = orden.replace("busca en chatgpt", "").strip()
            motor = "chatgpt"
        else:
            return False
    else:
        consulta = str(arg).strip()
    if not consulta:
        print("No se proporcionó una consulta para la búsqueda.")
        return True
    consulta_encoded = urllib.parse.quote_plus(consulta)
    try:
        if motor == "google":
            url = f"https://www.google.com/search?q={consulta_encoded}"
            webbrowser.open(url)
            print(f"Buscando en Google: {consulta}")
        elif motor == "chatgpt":
            url = f"https://chat.openai.com/?q={consulta_encoded}"
            webbrowser.open(url)
            print(f"Abriendo ChatGPT con la consulta: {consulta}")
        else:
            print(f"Motor de búsqueda desconocido: {motor}")
        return True
    except Exception as e:
        print(f"Error al abrir el navegador para la búsqueda: {e}")
        return True

def palabra_a_numero_extractor(texto):
    numeros = {
        "cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
        "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
        "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
        "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19,
        "veinte": 20, "veintiuno": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24,
        "veinticinco": 25, "veintiseis": 26, "veintisiete": 27, "veintiocho": 28,
        "veintinueve": 29, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
        "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90, "cien": 100
    }
    resultados = {}
    for palabra in numeros.keys():
        if palabra in texto:
            resultados[palabra] = numeros[palabra]
    patron = r"(\w+)\s+y\s+(\w+)"
    compuestos = re.findall(patron, texto)
    for p1, p2 in compuestos:
        n1 = numeros.get(p1, None)
        n2 = numeros.get(p2, None)
        if n1 is not None and n2 is not None:
            resultados[f"{p1} y {p2}"] = n1 + n2
    return resultados

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    return texto

def procesar_comando(texto, apps_dict):
    texto = normalizar_texto(texto).strip()

    # Cerrar asistente
    if any(palabra in texto for palabra in ["adios", "hasta la proxima", "finaliza"]):
        print("Cerrando Cosmo... ¡Hasta luego!")
        sys.exit(0)

    # Subir/bajar volumen
    m_subir = re.search(r"(sube el volumen a|suba el volumen a|sube volumen a|aumenta volumen a) (\d+)%?", texto)
    m_bajar = re.search(r"(baja el volumen a|baja volumen a|disminuye volumen a) (\d+)%?", texto)
    if m_subir:
        set_volume(int(m_subir.group(2)))
        return True
    if m_bajar:
        set_volume(int(m_bajar.group(2)))
        return True
    for kw in ["sube el volumen a", "suba el volumen a", "sube volumen a", "aumenta volumen a"]:
        if kw in texto:
            for palabra, num in palabra_a_numero_extractor(texto).items():
                set_volume(num)
                return True
    for kw in ["baja el volumen a", "baja volumen a", "disminuye volumen a"]:
        if kw in texto:
            for palabra, num in palabra_a_numero_extractor(texto).items():
                set_volume(num)
                return True

    # Pausa/continua reproducción
    if any(p in texto for p in ["pausa", "pause"]):
        pyautogui.press('playpause')
        print("Reproducción pausada")
        return True
    if any(p in texto for p in ["continua", "reanuda"]):
        pyautogui.press('playpause')
        print("Reproducción reanudada")
        return True

    # Abrir apps
    if texto.startswith("abre "):
        abrir_app(texto[5:].strip(), apps_dict)
        return True

    # Reproducir música
    m_reproduce = re.match(r"reproduce (.+) en (spotify|youtube)", texto)
    if m_reproduce:
        cancion, plataforma = m_reproduce.group(1).strip(), m_reproduce.group(2).strip()
        if plataforma == "spotify":
            spotify_path = shutil.which("spotify")
            if spotify_path:
                spotify_running = any(p.name().lower() == "spotify.exe" for p in psutil.process_iter())
                if not spotify_running:
                    subprocess.Popen([spotify_path])
                    print("Abriendo Spotify...")
                    time.sleep(5)
                pyautogui.hotkey('ctrl', 'l')
                time.sleep(0.5)
                pyautogui.typewrite(cancion)
                pyautogui.press('enter')
                time.sleep(0.5)
                pyautogui.press('enter')
                print(f"Buscando y reproduciendo '{cancion}' en Spotify...")
            else:
                print("Spotify no está instalado o no se encuentra en PATH.")
        elif plataforma == "youtube":
            query = urllib.parse.quote_plus(cancion)
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            print(f"Buscando '{cancion}' en YouTube...")
        return True

    # Búsquedas
    if texto.startswith("busca en google"):
        procesar_busqueda(texto.replace("busca en google", "").strip(), motor="google")
        return True
    if texto.startswith("busca en chatgpt"):
        procesar_busqueda(texto.replace("busca en chatgpt", "").strip(), motor="chatgpt")
        return True

    print("Comando no reconocido o no soportado.")
    return False
