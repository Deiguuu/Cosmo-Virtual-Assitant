import { contextBridge } from "electron";
import { spawn } from "child_process";
import { electronAPI } from "@electron-toolkit/preload";

// Custom APIs for renderer
const api = {};

// Método para ejecutar el asistente Python en una terminal nueva
api.ejecutarAsistente = () => {
  const pythonPath = "C:\\Users\\droqu\\Documents\\CODES\\STT-Vosk-Project\\src\\main.py";

  // Abrimos CMD usando start cmd /k para mantener la ventana abierta
  spawn("cmd.exe", ["/c", "start", "cmd", "/k", "python", pythonPath], {
    cwd: "C:\\Users\\droqu\\Documents\\CODES\\STT-Vosk-Project\\src", // asegura que main.py encuentre config.json
    detached: true, // la terminal queda independiente de Electron
    stdio: "inherit", // muestra la salida de Python en la terminal real
  });
};

// Exponemos las APIs al renderer
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", electronAPI);
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  window.electron = electronAPI;
  window.api = api;
}
