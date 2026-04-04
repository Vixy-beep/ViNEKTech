"""
Script para descargar imágenes corregidas de productos específicos
Algunos productos descargan mal de Amazon, estos se buscan manualmente
"""

import os
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-US,es;q=0.9,en;q=0.8",
}

# Productos que necesitan búsqueda en Google Images o AliExpress
PRODUCTOS_CORREGIR = [
    {
        "slug": "scada-test-device",
        "search": "SCADA test device industrial",
        "source": "aliexpress"  # AliExpress tiene mejores imágenes
    },
    {
        "slug": "network-packet-analyzer-device",
        "search": "Network packet analyzer hardware ethernet",
        "source": "aliexpress"
    },
    {
        "slug": "wifi-pineapple",
        "search": "Hak5 WiFi Pineapple Mark VII",
        "source": "official"  # Buscar en sitio oficial
    },
    {
        "slug": "network-tap-hardware",
        "search": "network tap hardware ethernet monitoring",
        "source": "aliexpress"
    },
]


def buscar_en_aliexpress(query):
    """Busca imagen en AliExpress"""
    url = f"https://www.aliexpress.com/wholesale?SearchText={requests.utils.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Buscar imagen de producto
        img_tags = soup.select("img.DCFmg")
        if img_tags:
            return img_tags[0].get("src")
    except Exception as e:
        print(f"  [!] Error en AliExpress: {e}")
    return None


def descargar_imagen(url_img, ruta_destino):
    """Descarga imagen a archivo"""
    try:
        r = requests.get(url_img, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(ruta_destino, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  [!] Error descargando: {e}")
    return False


def main():
    base_dir = "static/img/products"
    os.makedirs(base_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Corrector de imágenes - ViNEK Cybersecurity")
    print(f"{'='*60}\n")

    for i, producto in enumerate(PRODUCTOS_CORREGIR, 1):
        slug = producto["slug"]
        search = producto["search"]
        source = producto["source"]
        ruta = os.path.join(base_dir, f"{slug}.jpg")

        print(f"[{i}/{len(PRODUCTOS_CORREGIR)}] 🔍 Buscando: {slug}")
        print(f"   Query: {search}")
        print(f"   Fuente: {source}")

        if source == "aliexpress":
            url_img = buscar_en_aliexpress(search)
        else:
            print(f"   ⏭  {source} requiere búsqueda manual")
            continue

        if url_img:
            ok = descargar_imagen(url_img, ruta)
            if ok:
                print(f"   ✅ Descargado: {slug}.jpg")
            else:
                print(f"   ❌ Error al descargar")
        else:
            print(f"   ❌ No se encontró imagen")

    print(f"\n{'='*60}")
    print("Tip: Para imágenes que no se encuentren automáticamente,")
    print("descárgalas manualmente desde:")
    print("  - https://www.aliexpress.com")
    print("  - https://www.google.com/images")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
