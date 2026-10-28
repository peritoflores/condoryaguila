import json
import re
import os
from openai import OpenAI
from idiomas_data import idiomas_destino



# Inicializar el cliente de OpenAI (toma la API Key de las variables de entorno)
client = OpenAI()

# =====================================================================
# ⚙️ ZONA DE CONFIGURACIÓN
# =====================================================================
# Ruta de tu archivo 'es.js' de origen
RUTA_ES_JS = "../translations/es.js"  # O pon la ruta relativa como "../translations/es.js"

# Carpeta donde se guardarán los archivos de salida traducidos
DIRECTORIO_SALIDA = "../translations/"  # Carpeta actual o una específica como "../translations/"



# =====================================================================

def seleccionar_modelo():
    """Permite elegir el modelo de OpenAI de forma rápida."""
    print("=========================================================")
    print("🤖 SELECCIONA EL MODELO DE OPENAI (JS)")
    print("=========================================================")
    print("1. gpt-4o      (Máxima calidad)")
    print("2. gpt-4o-mini (Más rápido y económico - Recomendado)")
    print("---------------------------------------------------------")
    opcion = input("Elige el modelo (1 o 2, por defecto 2): ").strip()
    return "gpt-4o" if opcion == "1" else "gpt-4o-mini"

def traducir_archivo_js():
    # 1. Seleccionar modelo
    modelo_elegido = seleccionar_modelo()
    print(f"\n🚀 Usando modelo: [{modelo_elegido}]")

    # 2. Leer el archivo es.js desde la ruta configurada
    try:
        with open(RUTA_ES_JS, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{RUTA_ES_JS}'. Verifica la ruta.")
        return

    # Extraer el objeto JSON interno dentro de window.translations.es
    match = re.search(r'window\.translations\.es\s*=\s*({.*?});', contenido, re.DOTALL)
    if not match:
        print(f"❌ Error: No se pudo parsear el formato del archivo '{RUTA_ES_JS}'.")
        return

    translations_es = json.loads(match.group(1))

    # Asegurarse de que el directorio de salida exista
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

    print(f"\n🌐 Iniciando traducción del archivo JS a los 4 idiomas principales...")

    # 3. Iterar sobre los 4 idiomas
    for code_lang, info in idiomas_destino.items():
        filename = info["archivo"]
        nombre_idioma = info["nombre"]
        ruta_salida = os.path.join(DIRECTORIO_SALIDA, filename)

        print(f"\n🌐 Traduciendo al [{nombre_idioma.upper()}] -> Guardando en '{ruta_salida}'...")

        prompt = f"""
        Eres un traductor experto en localización de software y contenido místico/técnico.
        Traduce los valores del siguiente diccionario JSON del español al idioma '{nombre_idioma}' (código '{code_lang}').

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
                model=modelo_elegido,
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
                f"window.translations.{code_lang} = {json.dumps(translated_dict, ensure_ascii=False, indent=2)};\n"
            )

            # Guardar el archivo resultante en la ruta configurada
            with open(ruta_salida, "w", encoding="utf-8") as out_f:
                out_f.write(js_content)

            print(f"   ✅ ¡'{filename}' generado con éxito!")

        except Exception as e:
            print(f"   ❌ Error al procesar {nombre_idioma}: {e}")

    print("\n🎉 ¡Proceso de traducción JS completado con éxito!")

if __name__ == "__main__":
    traducir_archivo_js()