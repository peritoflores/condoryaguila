import json
import re
import os

def extraer_entornos_latex(ruta_tex):
    """Paso 1: Lee el archivo .tex y extrae las claves y contenidos sin modificar."""
    try:
        with open(ruta_tex, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo en '{ruta_tex}'.")
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
        texto_modificado = re.sub(r'\\enquote\{([^}]*)\}', r'\1', texto_modificado)

        
        # 2. Eliminar cualquier barra invertida sobrante (\ o \\)
        texto_modificado = re.sub(r'\\+', ' ', texto_modificado)
        
        # 3. Limpieza de espacios múltiples resultantes
        texto_modificado = re.sub(r'\s+', ' ', texto_modificado).strip()
        
        datos_limpios[clave] = texto_modificado

    return datos_limpios


def gestionar_index_idiomas(ruta_index=".."):
    """Lee el index, lista los idiomas actualmente traducidos, su cantidad y pide confirmación para limpiar."""
    ruta_json_idiomas = os.path.join(ruta_index, "idiomas_data.json")
    
    print(f"📖 Leyendo el registro de idiomas en: '{ruta_json_idiomas}'...")
    try:
        with open(ruta_json_idiomas, "r", encoding="utf-8") as f:
            idiomas = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo de idiomas en '{ruta_json_idiomas}'.")
        return False

    # 1. Identificar cuáles están actualmente traducidos antes del cambio
    traducidos_actuales = []
    for codigo, info in idiomas.items():
        if info.get("translated", False) == True:
            traducidos_actuales.append((codigo, info.get("nombre")))

    # 2. Mostrar la lista y la cantidad actual
    print("\n------------------------------------------------------------")
    print(f"📊 Idiomas actualmente traducidos (Total: {len(traducidos_actuales)}):")
    print("------------------------------------------------------------")
    if traducidos_actuales:
        for cod, nombre in traducidos_actuales:
            print(f"  • {nombre} ({cod})")
    else:
        print("  (Ningún idioma se encuentra marcado como traducido actualmente)")
    print("------------------------------------------------------------")
    print("⚠️ Esta acción limpiará los estados y dejará únicamente al español ('es') en true.")
    print("------------------------------------------------------------")

    # 3. Pedir confirmación al usuario antes de proceder
    confirmacion = input("¿Deseas continuar y aplicar la limpieza? (s/n): ").strip().lower()
    
    if confirmacion not in ['s', 'si', 'y']:
        print("⚠️ Operación cancelada por el usuario. No se modificó el archivo de idiomas.")
        return False

    # 4. Aplicar el cambio: solo español (es) en true, el resto en false
    for codigo, info in idiomas.items():
        info["translated"] = True if codigo == "es" else False

    # Guardar los cambios en el archivo
    with open(ruta_json_idiomas, "w", encoding="utf-8") as f:
        json.dump(idiomas, f, ensure_ascii=False, indent=4)
        
    print(f"✅ ¡El archivo '{ruta_json_idiomas}' ha sido actualizado y limpiado con éxito!")
    return True


def guardar_como_es_json(datos, ruta_salida):
    """Guarda el diccionario final formateado directamente como un archivo JSON puro."""
    if not datos:
        print("⚠️ No hay datos para guardar.")
        return

    directorio = os.path.dirname(ruta_salida)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(
        f"✅ ¡Archivo '{ruta_salida}' generado con éxito con {len(datos)} entradas procesadas en formato JSON!"
    )


if __name__ == "__main__":
    # ==========================================
    # RUTAS CONFIGURABLES INDEPENDIENTES
    # ==========================================
    RUTA_INDEX = ".."               # Ruta donde se ubica 'idiomas_data.json'
    RUTA_LATEX = "../latex"         # Ruta donde se ubica la carpeta y el archivo .tex
    RUTA_SALIDA = "../translations" # Ruta donde se guardará el 'es.json' resultante

    # Construcción de rutas completas
    archivo_tex = os.path.join(RUTA_LATEX, "CondoryAguila_ES.tex")
    archivo_json_salida = os.path.join(RUTA_SALIDA, "es.json")

    print("=== PASO 0: Gestión y actualización del índice de idiomas ===")
    proceder = gestionar_index_idiomas(ruta_index=RUTA_INDEX)

    if proceder:
        print(f"\nPaso 1: Leyendo y extrayendo de '{archivo_tex}'...")
        traducciones_crudas = extraer_entornos_latex(archivo_tex)

        if traducciones_crudas:
            print("Paso 2: Ejecutando loop de reemplazo de iconos...")
            traducciones_con_iconos = traducir_comandos_a_emojis(traducciones_crudas)

            print("Paso 3: Ejecutando loop aparte para limpiar formato...")
            traducciones_finales = limpiar_formato_latex(traducciones_con_iconos)

            print(f"Paso 4: Guardando en '{archivo_json_salida}'...")
            guardar_como_es_json(traducciones_finales, archivo_json_salida)