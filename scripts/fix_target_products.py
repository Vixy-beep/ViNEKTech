from pathlib import Path
import requests

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from store.models import Product

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-US,es;q=0.9,en;q=0.8",
}

OUT_DIR = Path("static/img/products")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_BY_SLUG = {
    "plunder-bug": "https://shop.hak5.org/products/plunder-bug",
    "network-packet-analyzer-device": "https://www.dualcomm.com/products/etap-2003-network-tap",
    "nitrokey-pro-2": "https://shop.nitrokey.com/shop/product/nitrokey-pro-2-3",
    "glinet-travel-router": "https://www.gl-inet.com/products/gl-mt300n-v2/",
}


def get_og_image(page_url: str):
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return None
        text = r.text
        markers = [
            'property="og:image" content="',
            'property="og:image:url" content="',
            "property='og:image' content='",
            "property='og:image:url' content='",
            'name="twitter:image" content="',
        ]
        for marker in markers:
            i = text.find(marker)
            if i == -1:
                continue
            start = i + len(marker)
            quote = '"' if marker.endswith('"') else "'"
            end = text.find(quote, start)
            if end == -1:
                continue
            return text[start:end]
    except Exception:
        return None
    return None


def download_image(url: str, dst: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if r.status_code == 200 and "image" in ctype and len(r.content) > 5000:
            dst.write_bytes(r.content)
            return True
    except Exception:
        return False
    return False


def update_translations():
    fixes = {
        "plunder-bug": {
            "name_es": "Interceptor de red Plunder Bug",
            "short_description_es": "Dispositivo Ethernet encubierto para captura de trafico en linea.",
        },
        "network-packet-analyzer-device": {
            "name_es": "Analizador de paquetes de red",
            "short_description_es": "Hardware dedicado para capturar y analizar trafico Ethernet.",
        },
        "glinet-travel-router": {
            "name_es": "Router de viaje GL.iNet",
        },
    }
    for slug, fields in fixes.items():
        p = Product.objects.filter(slug=slug).first()
        if not p:
            print(f"missing product for translation: {slug}")
            continue
        for k, v in fields.items():
            setattr(p, k, v)
        p.save(update_fields=list(fields.keys()) + ["updated_at"])
        print(f"updated translation: {slug}")


def main():
    replaced = 0
    failed = []

    for slug, page in PAGE_BY_SLUG.items():
        dst = OUT_DIR / f"{slug}.jpg"
        og = get_og_image(page)
        if og and download_image(og, dst):
            replaced += 1
            print(f"image replaced: {slug}")
        else:
            failed.append(slug)
            print(f"image FAILED: {slug}")

    update_translations()
    print(f"replaced={replaced}")
    print(f"failed={len(failed)}")
    if failed:
        print("failed_slugs=" + ",".join(failed))


if __name__ == "__main__":
    main()
