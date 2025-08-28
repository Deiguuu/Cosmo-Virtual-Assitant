# Cosmo - Asistente Virtual Inteligente

Cosmo es un **asistente virtual inteligente para Windows**, capaz de ejecutar aplicaciones, controlar el volumen del sistema, buscar información en Internet, reproducir música en YouTube y Spotify, y realizar otras tareas mediante **comandos de voz o texto**.  

El proyecto está diseñado para ser extensible y personalizable, permitiendo agregar nuevas funciones y comandos fácilmente.

---

## Características

- **Activación por voz** (requiere integración con tu motor STT).  
- **Control de aplicaciones**: abrir Word, Excel, Calculadora, Configuración, entre otros.  
- **Control de volumen** del sistema.  
- **Reproducción de música**:
  - YouTube (automática con pywhatkit).  
  - Spotify (requiere instalación y configuración).  
- **Búsquedas en Internet**:
  - Google
  - ChatGPT  
- **Gestión de comandos** mediante texto o voz.  
- **Sistema de alias** para ejecutar aplicaciones fácilmente.  
- Compatible con **Windows 10/11**.  

---

## Requisitos

- Python 3.10 o superior  
- Windows 10/11  
- Conexión a Internet (para búsquedas y reproducción de YouTube/Spotify)  

**Dependencias principales**:

```bash
pip install pywhatkit spotipy pycaw comtypes pyautogui psutil
