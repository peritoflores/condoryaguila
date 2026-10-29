import json
import re
import os

def extraer_entornos_latex(ruta_tex):
    """Paso 1: Lee el archivo .tex y extrae las claves y contenidos sin modificar."""
    try:
        with open(ruta_tex, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo '{ruta_tex}'.")
        return None

    patron = r"\\begin\{extraer\}\{([^}]+)\}(.*?)\\end\{extraer\}"
    coincidencias = re.findall(patron, contenido, re.DOTALL)

    datos_crudos = {}
    for clave, texto in coincidencias:
        datos_crudos[clave.strip()] = texto.strip()

    return datos_crudos


def traducir_comandos_a_emojis(datos):
    """Paso 2: Loop para recorrer los textos y reemplazar comandos por iconos."""
    mapeo_iconos = {
        r"\corazonrojo": "❤️",
        r"\cerebro": "🧠",
        r"\cruz": "✝️",
        r"\cruzinvertida": "┻",
        r"\langle": "⟨",
        r"\rangle": "⟩",
        r"\vert": "|",
        r"\mid": "|",
        r"\&": "&",
        r"$": "",
    }

    datos_procesados = {}
    for clave, texto in datos.items():
        texto_modificado = texto
        for comando, emoji in mapeo_iconos.items():
            patron_cmd = re.escape(comando) + r"(?![a-zA-Z])"
            texto_modificado = re.sub(patron_cmd, emoji, texto_modificado)
        datos_procesados[clave] = texto_modificado

    return datos_procesados


def limpiar_formato_latex(datos):
    """Paso 3: Loop aparte para retirar las barras dobles (\\\\) y el \\textbf."""
    datos_limpios = {}
    
    for clave, texto in datos.items():
        texto_modificado = texto
        
        # 1. Retirar las etiquetas de formato conservando únicamente el texto interior
        texto_modificado = re.sub(r'\\textbf\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\text\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\textit\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\enquote\{([^}]*)\}', r'\1', texto_modificado)
        
        # 2. Eliminar cualquier barra invertida sobrante (\ o \\)
        texto_modificado = re.sub(r'\\+', ' ', texto_modificado)
        
        # 3. Limpieza de espacios múltiples resultantes
        texto_modificado = re.sub(r'\s+', ' ', texto_modificado).strip()
        
        datos_limpios[clave] = texto_modificado

    return datos_limpios


def guardar_como_es_json(datos, ruta_salida="../translations/es.json"):
    """Guarda el diccionario final formateado directamente como un archivo JSON puro."""
    if not datos:
        print("⚠️ No hay datos para guardar.")
        return

    # Asegurarse de que el directorio de salida exista
    directorio = os.path.dirname(ruta_salida)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    # Guardar como JSON estructurado y limpio
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(
        f"✅ ¡Archivo '{ruta_salida}' generado con éxito con {len(datos)} entradas procesadas en formato JSON!"
    )


if __name__ == "__main__":
    archivo_tex = "../latex/CondoryAguila_ES.tex"
    archivo_json = "../translations/es.json"

    print(f"Paso 1: Leyendo y extrayendo de '{archivo_tex}'...")
    traducciones_crudas = extraer_entornos_latex(archivo_tex)

    if traducciones_crudas:
        print("Paso 2: Ejecutando loop de reemplazo de iconos...")
        traducciones_con_iconos = traducir_comandos_a_emojis(traducciones_crudas)

        print("Paso 3: Ejecutando loop aparte para limpiar formato...")
        traducciones_finales = limpiar_formato_latex(traducciones_con_iconos)

        print(f"Paso 4: Guardando en '{archivo_json}'...")
        guardar_como_es_json(traducciones_finales, archivo_json)