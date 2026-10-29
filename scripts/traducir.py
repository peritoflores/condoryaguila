import json
import os
from openai import OpenAI

# Inicializar el cliente de OpenAI (toma la API Key de las variables de entorno)
client = OpenAI()

# =====================================================================
# ⚙️ ZONA DE CONFIGURACIÓN
# =====================================================================

# 1. Cargar el archivo con la lista de idiomas disponibles
with open('../idiomas_data.json', 'r', encoding='utf-8') as f:
    idiomas_destino = json.load(f)

cantidad_idiomas = len(idiomas_destino)
print(f"Se cargaron {cantidad_idiomas} idiomas desde el archivo de configuración.")

# 2. Ruta de tu archivo 'es.json' de origen (fuente de las traducciones)
RUTA_ES_JSON = "../translations/es.json"  

# 3. Carpeta donde se guardarán los archivos JSON traducidos de salida
DIRECTORIO_SALIDA = "../translations/"  


# =====================================================================

def seleccionar_modelo():
    """Permite elegir el modelo de OpenAI de forma rápida."""
    print("\n=========================================================")
    print("🤖 SELECCIONA EL MODELO DE OPENAI")
    print("=========================================================")
    print("1. gpt-4o      (Máxima calidad)")
    print("2. gpt-4o-mini (Más rápido y económico - Recomendado)")
    print("---------------------------------------------------------")
    opcion = input("Elige el modelo (1 o 2, por defecto 2): ").strip()
    return "gpt-4o" if opcion == "1" else "gpt-4o-mini"


def seleccionar_idiomas(idiomas_dict):
    """Muestra la lista de idiomas en 3 columnas y permite seleccionar uno, un rango, varios o todos."""
    print("\n=================================================================")
    print("🌍 IDIOMAS DISPONIBLES")
    print("=================================================================")
    
    lista_claves = list(idiomas_dict.keys())
    total = len(lista_claves)
    
    # Organizar en 3 columnas
    columnas = 3
    filas = (total + columnas - 1) // columnas
    
    elementos_formateados = []
    for idx, (code_lang, info) in enumerate(idiomas_dict.items(), start=1):
        nombre = info.get("nombre", code_lang)
        celda = f"{idx:2d}. [{code_lang}] {nombre}"
        elementos_formateados.append(celda)
    
    # Imprimir en 3 columnas
    for f in range(filas):
        linea = ""
        for c in range(columnas):
            indice = f + c * filas
            if indice < total:
                linea += f"{elementos_formateados[indice]:<24} "
        print(linea)
    
    print("-----------------------------------------------------------------")
    print("Opciones de selección:")
    print(" • Un número (ej: 2) | Rango (ej: 1-5) | Varios (ej: 1, 4, 12)")
    print(" • Presiona ENTER o escribe 'todos' para seleccionar todos.")
    print("=================================================================")
    
    seleccion = input("Selecciona los idiomas: ").strip().lower()
    
    if not seleccion or seleccion == "todos" or seleccion == "t":
        return lista_claves
    
    idiomas_seleccionados = set()
    
    partes = seleccion.split(',')
    for parte in partes:
        parte = parte.strip()
        if '-' in parte:
            try:
                inicio, fin = map(int, parte.split('-'))
                for i in range(inicio, fin + 1):
                    if 1 <= i <= total:
                        idiomas_seleccionados.add(lista_claves[i - 1])
            except ValueError:
                print(f"⚠️ Rango inválido ignorado: '{parte}'")
        else:
            try:
                i = int(parte)
                if 1 <= i <= total:
                    idiomas_seleccionados.add(lista_claves[i - 1])
            except ValueError:
                print(f"⚠️ Selección inválida ignorada: '{parte}'")
                
    if not idiomas_seleccionados:
        print("⚠️ No se reconoció ninguna selección válida. Se procesarán TODOS los idiomas.")
        return lista_claves
        
    return list(idiomas_seleccionados)


def traducir_json():
    # 1. Seleccionar primero los idiomas a traducir
    claves_a_traducir = seleccionar_idiomas(idiomas_destino)
    print(f"\n🎯 Idiomas seleccionados ({len(claves_a_traducir)}): {', '.join(claves_a_traducir)}")

    # 2. Seleccionar el modelo de IA
    modelo_elegido = seleccionar_modelo()
    print(f"\n🚀 Usando modelo: [{modelo_elegido}]")

    # 3. Leer directamente el archivo es.json de origen
    try:
        with open(RUTA_ES_JSON, "r", encoding="utf-8") as f:
            translations_es = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo fuente '{RUTA_ES_JSON}'. Verifica la ruta.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: El archivo '{RUTA_ES_JSON}' no es un JSON válido.")
        return

    # Asegurarse de que el directorio de salida exista
    os.makedirs(DIRECTORIO_SALIDA, exist_ok=True)

    print(f"\n🌐 Iniciando traducción y generación de archivos JSON...")

    # 4. Iterar únicamente sobre los idiomas seleccionados
    for code_lang in claves_a_traducir:
        info = idiomas_destino[code_lang]
        
        filename = f"{code_lang}.json"
        nombre_idioma = info.get("nombre", code_lang)
        ruta_salida = os.path.join(DIRECTORIO_SALIDA, filename)

        print(f"\n🌐 Traduciendo al [{nombre_idioma.upper()}] -> Guardando en '{ruta_salida}'...")

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

            # Guardar el JSON traducido directamente
            with open(ruta_salida, "w", encoding="utf-8") as out_f:
                json.dump(translated_dict, out_f, ensure_ascii=False, indent=2)

            print(f"    ✅ ¡'{filename}' generado con éxito!")

        except Exception as e:
            print(f"    ❌ Error al procesar {nombre_idioma}: {e}")

    print("\n🎉 ¡Proceso completado con éxito!")


if __name__ == "__main__":
    traducir_json()