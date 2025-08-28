import os
import json

RUTAS_BASE = [
    "C:\\Program Files",
    "C:\\Program Files (x86)"
]

# Guardar siempre junto al script
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "programas_index.json")

def indexar_programas(output_file=OUTPUT_FILE):
    index = {}
    for base in RUTAS_BASE:
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".exe"):
                    nombre = file.lower().replace(".exe", "").strip()
                    if nombre not in index:
                        index[nombre] = os.path.join(root, file)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Índice generado con {len(index)} programas en {output_file}")

if __name__ == "__main__":
    indexar_programas()
