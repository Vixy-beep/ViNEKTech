import requests
from pathlib import Path
from shutil import copyfile

from templates.descargarimagenes import PRODUCTOS

OUT_DIR = Path("static/img/products")
OUT_DIR.mkdir(parents=True, exist_ok=True)
BRAND_IMG = Path("static/img/brand/vinek-isotipo.png")

OG_PAGE_BY_SLUG = {
    "usb-rubber-ducky": "https://shop.hak5.org/products/usb-rubber-ducky",
    "bash-bunny": "https://shop.hak5.org/products/bash-bunny",
    "key-croc": "https://shop.hak5.org/products/key-croc",
    "wifi-pineapple": "https://shop.hak5.org/products/wifi-pineapple",
    "lan-turtle": "https://shop.hak5.org/products/lan-turtle",
    "packet-squirrel": "https://shop.hak5.org/products/packet-squirrel",
    "shark-jack": "https://shop.hak5.org/products/shark-jack",
    "screen-crab": "https://shop.hak5.org/products/screen-crab",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-US,es;q=0.9,en;q=0.8",
}


def is_valid_image(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 8000:
        return False
    sig = path.read_bytes()[:12]
    return (
        sig.startswith(b"\xff\xd8\xff")
        or sig.startswith(b"\x89PNG\r\n\x1a\n")
        or (sig[:4] == b"RIFF" and sig[8:12] == b"WEBP")
    )


def download(url: str, dst: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=25, allow_redirects=True)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if r.status_code == 200 and "image" in ctype and len(r.content) > 8000:
            dst.write_bytes(r.content)
            return True
    except Exception:
        return False
    return False


def get_og_image(page_url: str):
    try:
        r = requests.get(page_url, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return None
        text = r.text
        marker = 'property="og:image" content="'
        i = text.find(marker)
        if i == -1:
            marker = "property='og:image' content='"
            i = text.find(marker)
            if i == -1:
                return None
            start = i + len(marker)
            end = text.find("'", start)
            if end == -1:
                return None
            return text[start:end]
        start = i + len(marker)
        end = text.find('"', start)
        if end == -1:
            return None
        return text[start:end]
    except Exception:
        return None


def wikimedia_image(query: str):
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "iiurlwidth": 1200,
    }
    try:
        r = requests.get(url, params=params, timeout=25, headers=HEADERS)
        data = r.json()
        pages = (data.get("query") or {}).get("pages") or {}
        for p in pages.values():
            ii = p.get("imageinfo") or []
            if not ii:
                continue
            candidate = ii[0].get("thumburl") or ii[0].get("url")
            if candidate:
                return candidate
    except Exception:
        return None
    return None


def main():
    replaced_kit = 0
    fixed_bad = 0
    forced_hak5 = 0
    left_as_is = 0
    failed = []

    for slug, query, _cat in PRODUCTOS:
        dst = OUT_DIR / f"{slug}.jpg"

        if "kit" in slug:
            if BRAND_IMG.exists():
                kit_png = OUT_DIR / f"{slug}.png"
                copyfile(BRAND_IMG, kit_png)
                replaced_kit += 1
            else:
                failed.append((slug, "brand-logo-missing"))
            continue

        page = OG_PAGE_BY_SLUG.get(slug)
        if page:
            og = get_og_image(page)
            if og and download(og, dst):
                forced_hak5 += 1
                continue

        if is_valid_image(dst):
            left_as_is += 1
            continue

        alt = wikimedia_image(query)
        if alt and download(alt, dst):
            fixed_bad += 1
        else:
            failed.append((slug, "no-coherent-source"))

    print(f"forced_hak5={forced_hak5}")
    print(f"replaced_kit={replaced_kit}")
    print(f"fixed_bad={fixed_bad}")
    print(f"left_as_is={left_as_is}")
    print(f"failed={len(failed)}")
    for slug, reason in failed[:20]:
        print(f"- {slug}: {reason}")


if __name__ == "__main__":
    main()
