# server.py
import asyncio
import json
import websockets
from asistente import AsistenteVoz
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

console = Console()
asistente = None
asistente_task = None
connected_clients = set()
transcript_history = []  # Para mostrar las transcripciones en tiempo real

async def notify_clients(message):
    """Enviar mensajes a todos los clientes conectados"""
    if connected_clients:
        data = json.dumps(message)
        await asyncio.wait([client.send(data) for client in connected_clients])

def render_dashboard():
    """Crea un panel con el estado actual"""
    table = Table(expand=True)
    table.add_column("Elemento", justify="left", style="cyan")
    table.add_column("Estado", justify="left", style="magenta")

    table.add_row("Clientes conectados", str(len(connected_clients)))
    table.add_row("Asistente activo", "Sí" if asistente_task else "No")
    table.add_row("Transcripciones recientes", "\n".join(transcript_history[-5:]))

    panel = Panel(table, title="COSMO DASHBOARD", border_style="green")
    return panel

async def handler(websocket):
    global asistente, asistente_task
    connected_clients.add(websocket)
    console.log(f"[green][SERVER][/green] Cliente conectado. Total: {len(connected_clients)}")

    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            console.log(f"[blue][SERVER][/blue] Acción recibida: {action}")

            if action == "start" and not asistente_task:
                # Crear instancia del asistente y pasar notify_clients
                asistente = AsistenteVoz(notify_clients=notify_clients)
                asistente_task = asyncio.create_task(asistente.iniciar())
                console.log("[yellow][SERVER][/yellow] Asistente iniciado")
                await notify_clients({"status": "ACTIVO"})

            elif action == "stop" and asistente_task:
                asistente_task.cancel()
                asistente_task = None
                console.log("[red][SERVER][/red] Asistente detenido")
                await notify_clients({"status": "DETENIDO"})

            # Log de transcripción si viene del frontend
            if "transcript" in data:
                transcript_history.append(data["transcript"])
    finally:
        connected_clients.remove(websocket)
        console.log(f"[green][SERVER][/green] Cliente desconectado. Total: {len(connected_clients)}")

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        console.log("[green][SERVER][/green] Servidor WebSocket corriendo en ws://127.0.0.1:8765")
        with Live(render_dashboard(), refresh_per_second=1, console=console) as live:
            while True:
                live.update(render_dashboard())
                await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
