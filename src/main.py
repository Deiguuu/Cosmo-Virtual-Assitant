# main.py
from asistente import AsistenteVoz
import asyncio

if __name__ == "__main__":
    asistente = AsistenteVoz()  # No pasamos config, se carga dentro de la clase
    asyncio.run(asistente.iniciar())
