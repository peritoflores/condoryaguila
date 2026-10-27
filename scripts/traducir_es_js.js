import json
import re
import os
from openai import OpenAI

# Inicializar el cliente de OpenAI (toma automáticamente la API Key de las variables de entorno)
client = OpenAI()

# =====================================================================
# ⚙️ ZONA DE CONFIGURACIÓN DE RUTAS
# =====================================================================
# Ruta de tu archivo 'es.js' de origen (puede ser ruta relativa o absoluta)
RUTA_ES_JS = "../translations/es.js"  # Ejemplo: "src/i18n/es.js" o "C:/proyectos/es.js"

# Carpeta donde se guardarán los archivos de salida traducidos
DIRECTORIO_SALIDA = "../translations/"  # Ejemplo: "." (directorio actual) o "src/i18n"

# Diccionario de idiomas de destino y sus nombres de archivo
idiomas_destino = {
    "en": "en.js",
    "pt": "pt.js",
    "fr": "fr.js"
}
# =====================================================================

def traducir_archivo_js():
    # 1. Leer el archivo es.js desde la ruta configurada
    try:
        with open(RUTA_ES_JS, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{RUTA_ES_JS}'.")
        return

    # Extraer el objeto JSON interno dentro de window.translations.es
    match = re.search(r'window\.translations\.es\s*=\s*({.*?});', contenido, re.DOTALL)
    if not match:
        print(f"❌ Error: No se pudo parsear el formato del archivo '{RUTA_ES_JS}'.")
        return

    translations_es = json.loads(match.group(1))

    # Asegurarse de que el directorio de salida exista (lo crea si no existe)
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

    # 2. Iterar sobre cada idioma para realizar la traducción con OpenAI
    for lang, filename in idiomas_destino.items():
        # Combinar el directorio de salida con el nombre del archivo
        ruta_salida = os.path.join(DIRECTORIO_SALIDA, filename)
        
        print(f"🌐 Traduciendo contenido al idioma [{lang.upper()}] -> Guardando en '{ruta_salida}'...")

        prompt = f"""
        Eres un traductor experto en localización de software y contenido místico/técnico.
        Traduce los valores del siguiente diccionario JSON del español al idioma con código '{lang}'.

        REGLAS ESTRICTAS DE TRADUCCIÓN:
        1. NO modifiques las claves del diccionario (ej: 'condor_title', 'main_sub'), traduce únicamente los VALORES.
        2. Mantén intactos todos los emojis presentes (❤️, 🧠, ✝️, ┻).
        3. Mantén intactos los comandos y estructuras de LaTeX (como $\\vert ... \\rangle$, \\textbf{{...}}, \\textit{{...}}, \\enquote{{...}}, \\url{{...}}), traduciendo de forma natural solo el texto plano interno que contienen.
        4. Devuelve la respuesta exclusivamente en formato JSON válido (un objeto JSON con las mismas claves traducidas).

        Diccionario original en español:
        {json.dumps(translations_es, ensure_ascii=False, indent=2)}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # O puedes usar "gpt-4o-mini" según prefieras
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un asistente experto en traducción e internacionalización de archivos de localización JSON preservando sintaxis técnica y LaTeX."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            # Obtener y parsear el JSON devuelto por el modelo
            translated_dict = json.loads(response.choices[0].message.content)

            # Formatear la salida idéntica a tu estructura de es.js
            js_content = (
                "window.translations = window.translations || {};\n"
                f"window.translations.{lang} = {json.dumps(translated_dict, ensure_ascii=False, indent=2)};\n"
            )

            # Guardar el archivo resultante en la ruta de salida configurada
            with open(ruta_salida, "w", encoding="utf-8") as out_f:
                out_f.write(js_content)

            print(f"✅ ¡Archivo '{ruta_salida}' generado con éxito!")

        except Exception as e:
            print(f"❌ Error al procesar el idioma {lang}: {e}")

if __name__ == "__main__":
    traducir_archivo_js()