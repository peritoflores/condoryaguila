import asyncio
import json
import os
from openai import AsyncOpenAI

# Inicializar el cliente asíncrono de OpenAI (toma la API Key de las variables de entorno)
client = AsyncOpenAI()

# =====================================================================
# ⚙️ ZONA DE CONFIGURACIÓN
# =====================================================================

RUTA_IDIOMAS_DATA = "../idiomas_data.json"
RUTA_ES_JSON = "../translations/es.json"  
DIRECTORIO_SALIDA = "../translations/"  

# =====================================================================
# CÓDIGOS DE COLOR ANSI PARA CONSOLA
# =====================================================================
VERDE = "\033[92m"
AMARILLO = "\033[93m"
RESET = "\033[0m"


def seleccionar_modelo():
    """Selecciona el modelo de OpenAI (automático en GitHub Actions o manual en local)."""
    if not os.isatty(0):
        return "gpt-4o-mini"

    print("\n=========================================================")
    print("🤖 SELECCIONA EL MODELO DE OPENAI")
    print("=========================================================")
    print("1. gpt-4o      (Máxima calidad)")
    print("2. gpt-4o-mini (Más rápido y económico - Recomendado)")
    print("---------------------------------------------------------")
    opcion = input("Elige el modelo (1 o 2, por defecto 2): ").strip()
    return "gpt-4o" if opcion == "1" else "gpt-4o-mini"


def obtener_idiomas_a_procesar(idiomas_dict):
    """Devuelve todos los idiomas si es automático, o permite filtrar si es manual."""
    lista_claves = list(idiomas_dict.keys())
    total = len(lista_claves)

    # Entorno no interactivo (GitHub Actions): procesar todos automáticamente
    if not os.isatty(0):
        print("🤖 Entorno no interactivo detectado (GitHub Actions). Procesando TODOS los idiomas.")
        return [(i, lista_claves[i - 1]) for i in range(1, total + 1)]

    # Menú interactivo local
    print("\n=================================================================")
    print("🌍 IDIOMAS DISPONIBLES (Verde = Traducido, Amarillo = Pendiente)")
    print("=================================================================")
    
    elementos_formateados = []
    for idx, (code_lang, info) in enumerate(idiomas_dict.items(), start=1):
        nombre = info.get("nombre", code_lang)
        ya_traducido = info.get("translated", False)
        estado_str = f"{VERDE}[TRADUCIDO]{RESET}" if ya_traducido else f"{AMARILLO}[PENDIENTE]{RESET}"
        elementos_formateados.append(f"{idx:2d}. [{code_lang}] {nombre} {estado_str}")
    
    columnas = 3
    filas = (total + columnas - 1) // columnas
    for f in range(filas):
        linea = ""
        for c in range(columnas):
            indice = f + c * filas
            if indice < total:
                linea += f"{elementos_formateados[indice]:<42} "
        print(linea)
    
    print("-----------------------------------------------------------------")
    seleccion = input("Selecciona los idiomas (ENTER para todos): ").strip().lower()
    
    if not seleccion or seleccion in ["todos", "t"]:
        return [(i, lista_claves[i - 1]) for i in range(1, total + 1)]
    
    indices_seleccionados = []
    for parte in seleccion.split(','):
        parte = parte.strip()
        if '-' in parte:
            try:
                inicio, fin = map(int, parte.split('-'))
                indices_seleccionados.extend([i for i in range(inicio, fin + 1) if 1 <= i <= total])
            except ValueError:
                pass
        else:
            try:
                i = int(parte)
                if 1 <= i <= total:
                    indices_seleccionados.append(i)
            except ValueError:
                pass
                
    if not indices_seleccionados:
        return [(i, lista_claves[i - 1]) for i in range(1, total + 1)]
    
    indices_seleccionados = sorted(list(set(indices_seleccionados)))
    return [(i, lista_claves[i - 1]) for i in indices_seleccionados]


async def traducir_un_idioma(numero_id, code_lang, info, translations_es, modelo_elegido):
    """Traduce un idioma de manera asíncrona y devuelve el código si tuvo éxito."""
    filename = f"{code_lang}.json"
    nombre_idioma = info.get("nombre", code_lang)
    ruta_salida = os.path.join(DIRECTORIO_SALIDA, filename)

    print(f"🌐 [{numero_id}] Iniciando traducción al [{nombre_idioma.upper()}]...")

    prompt = f"""
    Eres un traductor experto en localización de contenido místico/técnico.
    Traduce los valores del siguiente diccionario JSON del español al idioma '{nombre_idioma}' (código '{code_lang}').

    REGLAS ESTRICTAS DE TRADUCCIÓN:
    1. NO modifiques las claves del diccionario (ej: 'condor_title', 'main_sub'), traduce únicamente los VALORES.
    2. Mantén intactos todos los emojis presentes (❤️, 🧠, ✝️, ┻).
    3. Mantén intactos los comandos y estructuras de LaTeX (como $\\vert ... \\rangle$, \\textbf{{...}}, \\textit{{...}}), traduciendo de forma natural solo el texto plano interno que contienen.
    4. Devuelve la respuesta exclusivamente en formato JSON válido (un objeto JSON con las mismas claves traducidas).

    Diccionario original en español:
    {json.dumps(translations_es, ensure_ascii=False, indent=2)}
    """

    try:
        response = await client.chat.completions.create(
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

        translated_dict = json.loads(response.choices[0].message.content)

        # Guardar el archivo JSON traducido individual
        with open(ruta_salida, "w", encoding="utf-8") as out_f:
            json.dump(translated_dict, out_f, ensure_ascii=False, indent=2)

        print(f"    ✅ [{numero_id}] ¡'{filename}' generado con éxito!")
        return code_lang, True  # Retornamos éxito

    except Exception as e:
        print(f"    ❌ [{numero_id}] Error al procesar {nombre_idioma}: {e}")
        return code_lang, False


async def main():
    # 1. Cargar configuración de idiomas
    try:
        with open(RUTA_IDIOMAS_DATA, 'r', encoding='utf-8') as f:
            idiomas_destino = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró '{RUTA_IDIOMAS_DATA}'.")
        return

    print(f"Se cargaron {len(idiomas_destino)} idiomas desde la configuración.")

    # 2. Seleccionar idiomas y modelo
    pares_a_traducir = obtener_idiomas_a_procesar(idiomas_destino)
    modelo_elegido = seleccionar_modelo()
    print(f"\n🚀 Usando modelo: [{modelo_elegido}] | Idiomas a procesar: {len(pares_a_traducir)}")

    # 3. Leer archivo fuente es.json
    try:
        with open(RUTA_ES_JSON, "r", encoding="utf-8") as f:
            translations_es = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo fuente '{RUTA_ES_JSON}'.")
        return

    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

    print(f"\n🌐 Lanzando traducciones en paralelo (todos a la vez)...")
    inicio = asyncio.get_event_loop().time()

    # 4. Lanzar todas las peticiones en paralelo
    tareas = [
        traducir_un_idioma(num, code, idiomas_destino[code], translations_es, modelo_elegido)
        for num, code in pares_a_traducir
    ]

    resultados = await asyncio.gather(*tareas)

    # 5. Actualizar y guardar 'idiomas_data.json' de una sola vez al terminar todos
    for code_lang, exito in resultados:
        if exito:
            idiomas_destino[code_lang]["translated"] = True

    with open(RUTA_IDIOMAS_DATA, "w", encoding="utf-8") as f_data:
        json.dump(idiomas_destino, f_data, ensure_ascii=False, indent=4)

    fin = asyncio.get_event_loop().time()
    print(f"\n🎉 ¡Proceso completado en {fin - inicio:.2f} segundos! Archivo de configuración actualizado.")


if __name__ == "__main__":
    asyncio.run(main())