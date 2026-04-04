#!/usr/bin/env python
"""Generar favicon.ico desde vinek-logo.png"""

from PIL import Image
import os

# Rutas
logo_path = "static/img/brand/vinek-logo.png"
favicon_path = "static/favicon.ico"

# Abrir imagen y crear favicon en múltiples tamaños
img = Image.open(logo_path)

# Convertir a RGBA si no lo es
if img.mode != "RGBA":
    img = img.convert("RGBA")

# Crear favicon con múltiples tamaños
sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
icon_sizes = []

for size in sizes:
    # Redimensionar manteniendo aspect ratio
    img_resized = img.copy()
    img_resized.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Crear canvas del tamaño correcto con fondo transparente
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img_resized.width) // 2, (size[1] - img_resized.height) // 2)
    canvas.paste(img_resized, offset, img_resized)
    
    icon_sizes.append(canvas)

# Guardar como favicon.ico
icon_sizes[0].save(favicon_path, format="ICO", sizes=[size for size in sizes])
print(f"✅ Favicon creado: {favicon_path}")
