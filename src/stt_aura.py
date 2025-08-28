import os
import sys
import queue
import time
import json
import sounddevice as sd
import vosk
import subprocess

# Ruta base y modelo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "models", "vosk-model-es-0.42"))

SAMPLE_RATE = 16000
WAKE_WORD = "cosmo"
COMMAND_TIMEOUT = 5  # segundos para esperar comando tras activación

audio_queue = queue.Queue()

APPS = {
    "bloc de notas": "notepad",
    "calculadora": "calc",
    "chrome": "chrome",
    "word": "winword",
    "paint": "mspaint",
    "explorador": "explorer",
    "cmd": "cmd",
}

def abrir_app(nombre_app):
    comando = APPS.get(nombre_app, nombre_app)  # usa nombre directo si no está en el diccionario
    try:
        subprocess.Popen([comando])
        print(f"Abriendo {comando}...")
    except FileNotFoundError:
        print(f"No se pudo encontrar la aplicación: {comando}")
    except Exception as e:
        print(f"Error al abrir {comando}: {e}")

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[Audio callback error] {status}", file=sys.stderr)
    audio_queue.put(bytes(indata))

def listen_for_commands(recognizer):
    activated = False
    last_activation_time = 0

    print("Sistema iniciado. Di 'COSMO' para activar la escucha de comandos.")

    while True:
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip().lower()
            if text:
                print(f"[Reconocido]: {text}")

                if not activated and WAKE_WORD in text:
                    activated = True
                    last_activation_time = time.time()
                    print("\n>>> Activado: habla tu comando ahora <<<\n")

                elif activated:
                    print(f">>> Comando recibido: {text}\n")

                    # Detectar comando "abre <app>"
                    if text.startswith("abre "):
                        nombre_app = text[5:].strip()
                        abrir_app(nombre_app)
                    else:
                        print("Comando no reconocido o no es para abrir aplicación.")

                    activated = False
                    print("Esperando 'COSMO' para activar de nuevo...\n")

        else:
            # Resultados parciales opcional
            partial = json.loads(recognizer.PartialResult())
            # Si quieres ver parciales, descomenta:
            # print(f"[Parcial]: {partial.get('partial','')}", end='\r')

        # Timeout automático
        if activated and (time.time() - last_activation_time > COMMAND_TIMEOUT):
            print("\n>>> Timeout: No se recibió comando. Desactivando...\n")
            activated = False
            print("Esperando 'AURA' para activar de nuevo...\n")

def main():
    print(f"Cargando modelo desde: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: La ruta del modelo no existe o es incorrecta:\n{MODEL_PATH}")
        sys.exit(1)

    try:
        model = vosk.Model(MODEL_PATH)
    except Exception as e:
        print(f"ERROR al cargar el modelo Vosk: {e}")
        sys.exit(1)

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                               channels=1, callback=audio_callback):
            listen_for_commands(recognizer)
    except KeyboardInterrupt:
        print("\nPrograma terminado por usuario.")
    except Exception as e:
        print(f"Error en el audio stream: {e}")

if __name__ == "__main__":
    main()
