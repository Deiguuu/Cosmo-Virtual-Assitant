import os
from vosk import Model

model_path = r"C:\Users\droqu\Documents\CODES\STT-Vosk-Project\models\vosk-model-es-0.42"

print(f"Intentando cargar modelo en: {model_path}")
if not os.path.isdir(model_path):
    print("Error: La ruta no es una carpeta válida.")
    exit(1)

try:
    model = Model(model_path)
    print("Modelo Vosk cargado correctamente.")
except Exception as e:
    print(f"Error cargando el modelo Vosk: {e}")
