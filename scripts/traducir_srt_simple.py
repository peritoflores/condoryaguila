import os
from openai import OpenAI

# Inicializar el cliente de OpenAI
client = OpenAI()

# =====================================================================
# ⚙️ ZONA DE CONFIGURACIÓN
# =====================================================================
RUTA_SRT = "es.srt"       # Ruta de tu archivo .srt original
DIRECTORIO_SALIDA = "."   # Carpeta donde se guardarán los resultados

# Los 4 idiomas principales para arrancar
idiomas_destino = {
    "en": {"archivo": "en.srt", "nombre": "Inglés"},
    "pt": {"archivo": "pt.srt", "nombre": "Portugués"},
    "fr": {"archivo": "fr.srt", "nombre": "Francés"},
    "de": {"archivo": "de.srt", "nombre": "Alemán"}
}
# =====================================================================

def seleccionar_modelo():
    """Permite elegir el modelo de OpenAI de forma rápida."""
    print("=========================================================")
    print("🤖 SELECCIONA EL MODELO DE OPENAI")
    print("=========================================================")
    print("1. gpt-4o      (Máxima calidad)")
    print("2. gpt-4o-mini (Más rápido y económico - Recomendado)")
    print("---------------------------------------------------------")
    opcion = input("Elige el modelo (1 o 2, por defecto 2): ").strip()
    return "gpt-4o" if opcion == "1" else "gpt-4o-mini"

def traducir_srt_4_idiomas():
    # 1. Seleccionar modelo
    modelo_elegido = seleccionar_modelo()
    print(f"\n🚀 Usando modelo: [{modelo_elegido}]")

    # 2. Leer archivo .srt de origen
    try:
        with open(RUTA_SRT, "r", encoding="utf-8") as f:
            contenido_srt = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{RUTA_SRT}'. Verifica la ruta.")
        return

    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

    print(f"\n🎬 Iniciando traducción de subtítulos a los 4 idiomas principales...")

    # 3. Iterar sobre los 4 idiomas
    for code_lang, info in idiomas_destino.items():
        filename = info["archivo"]
        nombre_idioma = info["nombre"]
        ruta_salida = os.path.join(DIRECTORIO_SALIDA, filename)

        print(f"\n🌐 Traduciendo al [{nombre_idioma.upper()}] -> Guardando en '{ruta_salida}'...")

        prompt = f"""
        Eres un traductor experto en localización de subtítulos audiovisuales y contenido místico/técnico.
        Traduce el contenido del siguiente archivo en formato SRT del español al idioma '{nombre_idioma}' (código '{code_lang}').

        REGLAS ESTRICTAS DE TRADUCCIÓN:
        1. NO modifiques de ninguna forma los números de índice de los subtítulos (ej. 1, 2, 3...).
        2. NO modifiques bajo ningún concepto las marcas de tiempo (formato estricto: HH:MM:SS,mmm --> HH:MM:SS,mmm).
        3. Traduce únicamente el texto hablado correspondiente a cada línea de subtítulo, adaptándolo de forma natural, fluida y con la brevedad adecuada para lectura en pantalla.
        4. Mantén intactos los términos clave o nombres propios (como Pneuma, Psyche, Gnosis, UNO, EGO, Yaldabaoth, Sofía, Pleroma).
        5. Devuelve EXCLUSIVAMENTE el resultado en formato SRT válido, respetando exactamente la estructura de bloques y líneas en blanco originales. No agregues texto de introducción ni conclusiones.

        Archivo SRT original en español:
        {contenido_srt}
        """

        try:
            response = client.chat.completions.create(
                model=modelo_elegido,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en subtitulado y traducción audiovisual que preserva estrictamente la estructura técnica de los archivos SRT."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            resultado_srt = response.choices[0].message.content.strip()

            # Limpieza por si el modelo incluye bloques de código markdown
            if resultado_srt.startswith("```"):
                lineas = resultado_srt.splitlines()
                if lineas[0].startswith("```"):
                    lineas = lineas[1:]
                if lineas and lineas[-1].startswith("```"):
                    lineas = lineas[:-1]
                resultado_srt = "\n".join(lineas).strip()

            with open(ruta_salida, "w", encoding="utf-8") as out_f:
                out_f.write(resultado_srt + "\n")

            print(f"   ✅ ¡'{filename}' generado con éxito!")

        except Exception as e:
            print(f"   ❌ Error al procesar {nombre_idioma}: {e}")

    print("\n🎉 ¡Proceso completado para los 4 idiomas principales!")

if __name__ == "__main__":
traducir_srt_4_idiomas()