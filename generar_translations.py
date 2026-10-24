from deep_translator import GoogleTranslator

# Texto que queremos traducir
texto_original = "¡Hola, mundo!"

# Creamos el traductor indicando el idioma de origen y el de destino
traductor = GoogleTranslator(source='es', target='en')

# Realizamos la traducción
texto_traducido = traductor.translate(texto_original)

# Mostramos los resultados
print(f"Texto original: {texto_original}")
print(f"Texto traducido: {texto_traducido}")