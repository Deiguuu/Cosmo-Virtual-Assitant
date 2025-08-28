# asistente.py
import os
import sys
import time
import json
import queue
import vosk
import sounddevice as sd
import unicodedata
import edge_tts
import asyncio
import pygame
from comandos import procesar_comando
from cosmo_respuestas import CosmoRespuestas
from rich import print

class AsistenteVoz:
    def __init__(self, config_path=None, notify_clients=None):
        # Ruta por defecto al config.json si no se pasa
        if config_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.json")
        
        # Cargar configuración
        try:
            with open(config_path, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"[red]Error al cargar configuración: {config_path} no existe[/red]")
            self.config = {
                "wake_word": "aura",
                "command_timeout": 10,
                "sample_rate": 16000,
                "apps": {}
            }

        self.wake_word = self.normalizar_texto(self.config.get("wake_word", "aura"))
        self.command_timeout = self.config.get("command_timeout", 10)
        self.sample_rate = self.config.get("sample_rate", 16000)
        self.apps = self.config.get("apps", {})

        # CORRECCIÓN: Ruta del modelo correcta
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # sube un nivel desde src
        self.model_path = os.path.join(base_dir, "models", "vosk-model-es-0.42")

        self.audio_queue = queue.Queue()
        self.voice = "es-AR-ElenaNeural"
        self.escuchando = True
        self.notify_clients = notify_clients
        pygame.mixer.init()
        self.cosmo_resp = CosmoRespuestas()

    def normalizar_texto(self, texto):
        texto = texto.lower()
        texto = unicodedata.normalize('NFD', texto)
        return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

    async def hablar(self, texto):
        self.escuchando = False
        print(f"[magenta][ASISTENTE][/magenta] {texto}")

        if self.notify_clients:
            await self.notify_clients({"status": "HABLANDO", "transcript": texto})

        communicate = edge_tts.Communicate(texto, self.voice)
        temp_file = "temp_voice.mp3"
        await communicate.save(temp_file)

        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
        os.remove(temp_file)
        self.escuchando = True

    async def cargar_modelo(self):
        if not os.path.exists(self.model_path):
            await self.hablar(f"No encontré el modelo en {self.model_path}")
            sys.exit(1)
        try:
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            print("[cyan][ASISTENTE][/cyan] Modelo cargado correctamente")
        except Exception as e:
            await self.hablar(f"Error cargando modelo: {e}")
            sys.exit(1)

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"[red][AUDIO][/red] {status}", file=sys.stderr)
        self.audio_queue.put(bytes(indata))

    async def procesar_comando(self, texto):
        procesado = procesar_comando(texto, self.apps)
        if not procesado:
            await self.hablar(self.cosmo_resp.get("error"))
        else:
            await self.hablar(self.cosmo_resp.get("confirmacion"))

    async def escuchar(self):
        activado = False
        tiempo_activacion = 0
        await self.hablar(self.cosmo_resp.get("saludo"))

        if self.notify_clients:
            await self.notify_clients({"status": "ESPERANDO_WAKEWORD"})

        while True:
            data = self.audio_queue.get()
            if not self.escuchando:
                continue

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                texto = result.get("text", "").strip().lower()
                texto_normalizado = self.normalizar_texto(texto)

                if texto:
                    print(f"[green][RECONOCIDO][/green] {texto}")

                    if self.notify_clients:
                        await self.notify_clients({"transcript": texto})

                    if not activado and self.wake_word in texto_normalizado:
                        activado = True
                        tiempo_activacion = time.time()
                        await self.hablar(self.cosmo_resp.get("activacion"))
                        if self.notify_clients:
                            await self.notify_clients({"status": "ACTIVO"})
                        continue

                    elif activado:
                        tiempo_activacion = time.time()
                        await self.procesar_comando(texto)
            else:
                _ = json.loads(self.recognizer.PartialResult())

            if activado and (time.time() - tiempo_activacion > self.command_timeout):
                await self.hablar("No recibí ningún comando. Diga la palabra clave para continuar.")
                activado = False
                if self.notify_clients:
                    await self.notify_clients({"status": "ESPERANDO_WAKEWORD"})

    async def iniciar(self):
        await self.cargar_modelo()
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self.audio_callback,
            ):
                await self.escuchar()
        except asyncio.CancelledError:
            print("[red][ASISTENTE][/red] Tarea cancelada")
            if self.notify_clients:
                await self.notify_clients({"status": "DETENIDO"})
        except KeyboardInterrupt:
            await self.hablar(self.cosmo_resp.get("despedida"))
        except Exception as e:
            await self.hablar(f"Error de audio: {e}")
