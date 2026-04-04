from pathlib import Path
import hashlib
import requests
from bs4 import BeautifulSoup

from templates.descargarimagenes import PRODUCTOS, HEADERS

BASE = Path("static/img/products")
BASE.mkdir(parents=True, exist_ok=True)


def img_hash(path: Path):
    return hashlib.md5(path.read_bytes()).hexdigest()


def is_real_image(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 9000:
        return False
    sig = path.read_bytes()[:12]
    return (
        sig.startswith(b"\xff\xd8\xff")
        or sig.startswith(b"\x89PNG\r\n\x1a\n")
        or (sig[:4] == b"RIFF" and sig[8:12] == b"WEBP")
    )


def amazon_candidates(query: str):
    url = f"https://www.amazon.com/s?k={requests.utils.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        found = []
        for tag in soup.select("img.s-image")[:12]:
            src = tag.get("src")
            if src and src.startswith("http"):
                found.append(src)
        return found
    except Exception:
        return []


def download(url: str, dst: Path) -> bool:
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        ctype = (r.headers.get("Content-Type") or "").lower()
        if r.status_code == 200 and "image" in ctype and len(r.content) >= 9000:
            dst.write_bytes(r.content)
            return True
    except Exception:
        return False
    return False


def main():
    products = {slug: query for slug, query, _ in PRODUCTOS}

    # Collect current hashes to detect duplicates.
    hash_to_slugs = {}
    for slug in products:
        p = BASE / f"{slug}.jpg"
        if p.exists():
            h = img_hash(p)
            hash_to_slugs.setdefault(h, []).append(slug)

    duplicates = set()
    for slugs in hash_to_slugs.values():
        if len(slugs) > 1:
            # Keep first, refresh rest.
            duplicates.update(slugs[1:])

    refreshed = 0
    failed = []

    for slug, query in products.items():
        # Kits use brand image in UI, skip file refresh.
        if "kit" in slug:
            continue

        dst = BASE / f"{slug}.jpg"
        needs_refresh = (not is_real_image(dst)) or (slug in duplicates)
        if not needs_refresh:
            continue

        tried = set()
        ok = False
        for q in [query, f"{query} hardware", f"{query} device"]:
            for cand in amazon_candidates(q):
                if cand in tried:
                    continue
                tried.add(cand)
                if download(cand, dst):
                    ok = True
                    break
            if ok:
                break

        if ok:
            refreshed += 1
        else:
            failed.append(slug)

    print(f"refreshed={refreshed}")
    print(f"failed={len(failed)}")
    if failed:
        print("failed_slugs=" + ",".join(failed))


if __name__ == "__main__":
    main()
