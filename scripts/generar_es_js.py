import json
import re


def extraer_entornos_latex(ruta_tex):
    """Paso 1: Lee el archivo .tex y extrae las claves y contenidos sin modificar[cite: 3]."""
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
    """Paso 2: Loop para recorrer los textos y reemplazar comandos por iconos[cite: 3]."""
    mapeo_iconos = {
        r"\corazonrojo": "❤️",
        r"\cerebro": "🧠",
        r"\cruz": "✝️",
        r"\cruzinvertida": "┻",
     #   r"\rangle$": "⟩",
      # Mapeos solicitados para LaTeX:
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
    """Paso 3: Loop aparte para retirar las barras dobles (\\\\) y el \\textbf[cite: 3]."""
    datos_limpios = {}
    
    for clave, texto in datos.items():
        texto_modificado = texto
        
        # 1. Retirar las etiquetas de formato conservando únicamente el texto interior
        texto_modificado = re.sub(r'\\textbf\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\text\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\textit\{([^}]*)\}', r'\1', texto_modificado)
        texto_modificado = re.sub(r'\\enquote\{([^}]*)\}', r'\1', texto_modificado) # Opcional para limpiar URLs
        
        # 2. Eliminar cualquier barra invertida sobrante (\ o \\)
        texto_modificado = re.sub(r'\\+', ' ', texto_modificado)
      
        
        # 3. Limpieza de espacios múltiples resultantes
        texto_modificado = re.sub(r'\s+', ' ', texto_modificado).strip()
        
        datos_limpios[clave] = texto_modificado

    return datos_limpios


def guardar_como_es_js(datos, ruta_salida="es.js"):
    """Guarda el diccionario final formateado en el archivo es.js[cite: 3]."""
    if not datos:
        print("⚠️ No hay datos para guardar.")
        return

    json_str = json.dumps(datos, ensure_ascii=False, indent=2)

    contenido_js = (
        "window.translations = window.translations || {};\n"
        f"window.translations.es = {json_str};\n"
    )

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(contenido_js)

    print(
        f"✅ ¡Archivo '{ruta_salida}' generado con éxito con {len(datos)} entradas procesadas!"
    )


if __name__ == "__main__":
    archivo_tex = "../latex/CondoryAguila_ES.tex"
    archivo_js = "../translations/es.js"

    print(f"Paso 1: Leyendo y extrayendo de '{archivo_tex}'[cite: 3]...")
    traducciones_crudas = extraer_entornos_latex(archivo_tex)

    if traducciones_crudas:
        print("Paso 2: Ejecutando loop de reemplazo de iconos[cite: 3]...")
        traducciones_con_iconos = traducir_comandos_a_emojis(traducciones_crudas)

        print("Paso 3: Ejecutando loop aparte para limpiar \\\\ y \\textbf[cite: 3]...")
        traducciones_finales = limpiar_formato_latex(traducciones_con_iconos)

        print(f"Paso 4: Guardando en '{archivo_js}'[cite: 3]...")
        guardar_como_es_js(traducciones_finales, archivo_js)
