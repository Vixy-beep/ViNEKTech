"""
Script: Descargador de imágenes de productos de ciberseguridad
Autor: ViNEK
Uso: python descargar_imagenes.py

Requisitos:
    pip install requests beautifulsoup4

Las imágenes se guardan en ./imagenes/<categoría>/<nombre-producto>.jpg
"""

import os
import time
import random
import requests
from bs4 import BeautifulSoup

# ─── HEADERS para simular un navegador real ───────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-US,es;q=0.9,en;q=0.8",
}

# ─── CATÁLOGO DE PRODUCTOS ────────────────────────────────────────────────────
PRODUCTOS = [
    # (slug, nombre_busqueda, categoría)
    ("usb-rubber-ducky",        "Hak5 USB Rubber Ducky",             "inyeccion-usb"),
    ("bash-bunny",              "Hak5 Bash Bunny Mark II",           "inyeccion-usb"),
    ("malduino",                "Malduino USB hacking",              "inyeccion-usb"),
    ("digispark-usb",           "Digispark USB microcontroller",     "inyeccion-usb"),
    ("keystroke-injector-usb",  "USB HID keystroke injector",        "inyeccion-usb"),
    ("key-croc",                "Hak5 Key Croc keylogger",           "inyeccion-usb"),

    ("alfa-awus036ach",         "Alfa AWUS036ACH wifi adapter",      "wifi-auditoria"),
    ("alfa-awus036nha",         "Alfa AWUS036NHA wifi adapter",      "wifi-auditoria"),
    ("tp-link-wn722n",          "TP-Link TL-WN722N v1 wifi adapter", "wifi-auditoria"),
    ("wifi-pineapple",          "Hak5 WiFi Pineapple Mark VII",      "wifi-auditoria"),
    ("glinet-travel-router",    "GL.iNet travel router",             "wifi-auditoria"),
    ("openwrt-router",          "OpenWRT router",                    "wifi-auditoria"),
    ("portable-vpn-router",     "GL.iNet Beryl VPN router",          "wifi-auditoria"),
    ("deauther-watch",          "DSTIKE Deauther Watch ESP8266",     "wifi-auditoria"),
    ("dstike-deauther-oled",    "DSTIKE Deauther OLED",              "wifi-auditoria"),

    ("flipper-zero",            "Flipper Zero multi-tool",           "rfid-nfc"),
    ("proxmark3-rdv4",          "Proxmark3 RDV4 RFID NFC",           "rfid-nfc"),
    ("chameleon-ultra",         "Chameleon Ultra RFID emulator",     "rfid-nfc"),
    ("acr122u-nfc-reader",      "ACR122U NFC reader writer",         "rfid-nfc"),
    ("rfid-cloner-kit",         "RFID cloner kit 125khz",            "rfid-nfc"),

    ("hackrf-one",              "HackRF One SDR",                    "radio-sdr"),
    ("rtl-sdr-dongle",          "RTL-SDR dongle v3",                 "radio-sdr"),
    ("yard-stick-one",          "Yard Stick One sub-GHz",            "radio-sdr"),
    ("lora-dev-board",          "LoRa dev board SX1278",             "radio-sdr"),
    ("drone-signal-analyzer",   "drone signal analyzer RF",          "radio-sdr"),

    ("ubertooth-one",           "Ubertooth One Bluetooth sniffer",   "bluetooth-zigbee"),
    ("bluetooth-sniffer",       "Bluetooth packet sniffer hardware", "bluetooth-zigbee"),
    ("zigbee-sniffer",          "Zigbee sniffer USB",                "bluetooth-zigbee"),

    ("lan-turtle",              "Hak5 LAN Turtle",                   "red-trafico"),
    ("packet-squirrel",         "Hak5 Packet Squirrel",              "red-trafico"),
    ("shark-jack",              "Hak5 Shark Jack",                   "red-trafico"),
    ("plunder-bug",             "Hak5 Plunder Bug LAN tap",          "red-trafico"),
    ("network-tap-hardware",    "network tap hardware ethernet",     "red-trafico"),
    ("network-packet-analyzer-device", "network packet analyzer hardware", "red-trafico"),
    ("industrial-network-sniffer", "industrial network sniffer SCADA", "red-trafico"),

    ("yubikey-5-nfc",           "YubiKey 5 NFC security key",        "llaves-seguridad"),
    ("solokey-security-key",    "SoloKey FIDO2 security key",        "llaves-seguridad"),
    ("nitrokey-pro-2",          "Nitrokey Pro 2",                    "llaves-seguridad"),
    ("nitrokey-storage-2",      "Nitrokey Storage 2",                "llaves-seguridad"),
    ("hardware-password-manager", "hardware password manager device", "llaves-seguridad"),

    ("faraday-bag",             "Faraday bag signal blocking",       "privacidad"),
    ("faraday-box",             "Faraday box RF shielding",          "privacidad"),
    ("usb-data-blocker",        "USB data blocker juice jacking",    "privacidad"),
    ("secure-charging-cable",   "secure charging cable no data",     "privacidad"),
    ("rf-signal-detector",      "RF signal detector bug detector",   "privacidad"),
    ("hidden-camera-detector",  "hidden camera detector",            "privacidad"),
    ("anti-spy-detector",       "anti spy detector RF camera",       "privacidad"),
    ("laptop-privacy-screen",   "laptop privacy screen filter",      "privacidad"),
    ("webcam-cover-slider",     "webcam cover slider privacy",       "privacidad"),
    ("screen-crab",             "Hak5 Screen Crab HDMI",             "privacidad"),

    ("encrypted-usb-drive",     "encrypted USB drive IronKey",       "almacenamiento"),
    ("usb-power-monitor",       "USB power monitor voltage",         "almacenamiento"),
    ("portable-secure-power-bank", "secure power bank portable",     "almacenamiento"),
    ("usb-protocol-analyzer",   "USB protocol analyzer hardware",    "almacenamiento"),
    ("multiport-usb-data-switch", "USB data switch multiport",       "almacenamiento"),

    ("logic-analyzer-usb",      "USB logic analyzer Saleae",         "hardware-hacking"),
    ("jtag-debugger",           "JTAG debugger hardware",            "hardware-hacking"),
    ("eeprom-programmer",       "EEPROM programmer chip",            "hardware-hacking"),
    ("bios-flash-programmer-ch341a", "CH341A BIOS flash programmer", "hardware-hacking"),
    ("esp8266-nodemcu",         "ESP8266 NodeMCU development board", "hardware-hacking"),
    ("esp32-dev-kit",           "ESP32 development kit board",       "hardware-hacking"),
    ("sim-card-reader-writer",  "SIM card reader writer",            "hardware-hacking"),
    ("ir-blaster-receiver-kit", "IR blaster receiver kit",           "hardware-hacking"),
    ("universal-remote-hacking-device", "universal remote control device", "hardware-hacking"),
    ("thermal-camera-module",   "thermal camera module",             "hardware-hacking"),

    ("raspberry-pi-4-4gb",      "Raspberry Pi 4 4GB",                "mini-computadoras"),
    ("raspberry-pi-5-8gb",      "Raspberry Pi 5 8GB",                "mini-computadoras"),
    ("raspberry-pi-zero-w",     "Raspberry Pi Zero W",               "mini-computadoras"),
    ("beaglebone-black",        "BeagleBone Black",                  "mini-computadoras"),
    ("intel-nuc-mini-pc",       "Intel NUC mini PC",                 "mini-computadoras"),
    ("nvidia-jetson-nano",      "NVIDIA Jetson Nano",                "mini-computadoras"),
    ("usb-armory-mk-ii",        "USB Armory Mk II",                  "mini-computadoras"),
    ("pwnagotchi-kit",          "Pwnagotchi Raspberry Pi kit",       "mini-computadoras"),

    ("hardware-firewall-appliance", "Protectli hardware firewall",   "seguridad-red"),
    ("secure-kvm-switch",       "secure KVM switch",                 "seguridad-red"),

    ("lock-pick-set",           "professional lock pick set",        "seguridad-fisica"),
    ("digital-door-lock-tester", "digital door lock tester",        "seguridad-fisica"),
    ("key-decoder-tool",        "key decoder tool",                  "seguridad-fisica"),

    ("scada-test-device",       "SCADA security testing device",     "iot-scada"),
    ("iot-security-testing-kit", "IoT security testing kit",         "iot-scada"),
    ("smart-home-pentest-kit",  "smart home pentest kit",            "iot-scada"),
]


# ─── FUNCIÓN: buscar imagen en Amazon ────────────────────────────────────────
def buscar_imagen_amazon(query):
    url = f"https://www.amazon.com/s?k={requests.utils.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar primera imagen de resultado
        img_tags = soup.select("img.s-image")
        if img_tags:
            return img_tags[0].get("src")

        # Fallback: buscar cualquier imagen de producto
        img_tags = soup.find_all("img", {"data-image-latency": "s-product-image"})
        if img_tags:
            return img_tags[0].get("src")

    except Exception as e:
        print(f"  [!] Error buscando en Amazon: {e}")
    return None


# ─── FUNCIÓN: descargar imagen ───────────────────────────────────────────────
def descargar_imagen(url_img, ruta_destino):
    try:
        r = requests.get(url_img, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(ruta_destino, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  [!] Error descargando imagen: {e}")
    return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    base_dir = "imagenes"
    os.makedirs(base_dir, exist_ok=True)

    total = len(PRODUCTOS)
    exito = 0
    fallidos = []

    print(f"\n{'='*55}")
    print(f"  Descargador de imágenes - ViNEK Cybersecurity")
    print(f"  Total de productos: {total}")
    print(f"{'='*55}\n")

    for i, (slug, query, categoria) in enumerate(PRODUCTOS, 1):
        carpeta = os.path.join(base_dir, categoria)
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"{slug}.jpg")

        # Si ya existe, skip
        if os.path.exists(ruta):
            print(f"[{i}/{total}] ⏭  Ya existe: {slug}")
            exito += 1
            continue

        print(f"[{i}/{total}] 🔍 Buscando: {query}")
        url_img = buscar_imagen_amazon(query)

        if url_img:
            ok = descargar_imagen(url_img, ruta)
            if ok:
                print(f"         ✅ Guardado: {categoria}/{slug}.jpg")
                exito += 1
            else:
                print(f"         ❌ No se pudo descargar la imagen")
                fallidos.append(slug)
        else:
            print(f"         ❌ No se encontró imagen en Amazon")
            fallidos.append(slug)

        # Pausa aleatoria para no ser bloqueado por Amazon
        time.sleep(random.uniform(2.5, 5.0))

    print(f"\n{'='*55}")
    print(f"  Completado: {exito}/{total} imágenes descargadas")
    if fallidos:
        print(f"\n  Fallidos ({len(fallidos)}):")
        for slug in fallidos:
            print(f"    - {slug}")
    print(f"{'='*55}\n")

    if fallidos:
        print("Tip: Para los fallidos, búscalos manualmente en:")
        print("  https://www.amazon.com o https://www.aliexpress.com\n")


if __name__ == "__main__":
    main()
"""
Script: Descargador de imágenes de productos de ciberseguridad
Autor: ViNEK
Uso: python descargar_imagenes.py

Requisitos:
    pip install requests beautifulsoup4

Las imágenes se guardan en ./imagenes/<categoría>/<nombre-producto>.jpg
"""

import os
import time
import random
import requests
from bs4 import BeautifulSoup

# ─── HEADERS para simular un navegador real ───────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-US,es;q=0.9,en;q=0.8",
}

# ─── CATÁLOGO DE PRODUCTOS ────────────────────────────────────────────────────
PRODUCTOS = [
    # (slug, nombre_busqueda, categoría)
    ("usb-rubber-ducky",        "Hak5 USB Rubber Ducky",             "inyeccion-usb"),
    ("bash-bunny",              "Hak5 Bash Bunny Mark II",           "inyeccion-usb"),
    ("malduino",                "Malduino USB hacking",              "inyeccion-usb"),
    ("digispark-usb",           "Digispark USB microcontroller",     "inyeccion-usb"),
    ("keystroke-injector-usb",  "USB HID keystroke injector",        "inyeccion-usb"),
    ("key-croc",                "Hak5 Key Croc keylogger",           "inyeccion-usb"),

    ("alfa-awus036ach",         "Alfa AWUS036ACH wifi adapter",      "wifi-auditoria"),
    ("alfa-awus036nha",         "Alfa AWUS036NHA wifi adapter",      "wifi-auditoria"),
    ("tp-link-wn722n",          "TP-Link TL-WN722N v1 wifi adapter", "wifi-auditoria"),
    ("wifi-pineapple",          "Hak5 WiFi Pineapple Mark VII",      "wifi-auditoria"),
    ("glinet-travel-router",    "GL.iNet travel router",             "wifi-auditoria"),
    ("openwrt-router",          "OpenWRT router",                    "wifi-auditoria"),
    ("portable-vpn-router",     "GL.iNet Beryl VPN router",          "wifi-auditoria"),
    ("deauther-watch",          "DSTIKE Deauther Watch ESP8266",     "wifi-auditoria"),
    ("dstike-deauther-oled",    "DSTIKE Deauther OLED",              "wifi-auditoria"),

    ("flipper-zero",            "Flipper Zero multi-tool",           "rfid-nfc"),
    ("proxmark3-rdv4",          "Proxmark3 RDV4 RFID NFC",           "rfid-nfc"),
    ("chameleon-ultra",         "Chameleon Ultra RFID emulator",     "rfid-nfc"),
    ("acr122u-nfc-reader",      "ACR122U NFC reader writer",         "rfid-nfc"),
    ("rfid-cloner-kit",         "RFID cloner kit 125khz",            "rfid-nfc"),

    ("hackrf-one",              "HackRF One SDR",                    "radio-sdr"),
    ("rtl-sdr-dongle",          "RTL-SDR dongle v3",                 "radio-sdr"),
    ("yard-stick-one",          "Yard Stick One sub-GHz",            "radio-sdr"),
    ("lora-dev-board",          "LoRa dev board SX1278",             "radio-sdr"),
    ("drone-signal-analyzer",   "drone signal analyzer RF",          "radio-sdr"),

    ("ubertooth-one",           "Ubertooth One Bluetooth sniffer",   "bluetooth-zigbee"),
    ("bluetooth-sniffer",       "Bluetooth packet sniffer hardware", "bluetooth-zigbee"),
    ("zigbee-sniffer",          "Zigbee sniffer USB",                "bluetooth-zigbee"),

    ("lan-turtle",              "Hak5 LAN Turtle",                   "red-trafico"),
    ("packet-squirrel",         "Hak5 Packet Squirrel",              "red-trafico"),
    ("shark-jack",              "Hak5 Shark Jack",                   "red-trafico"),
    ("plunder-bug",             "Hak5 Plunder Bug LAN tap",          "red-trafico"),
    ("network-tap-hardware",    "network tap hardware ethernet",     "red-trafico"),
    ("network-packet-analyzer-device", "network packet analyzer hardware", "red-trafico"),
    ("industrial-network-sniffer", "industrial network sniffer SCADA", "red-trafico"),

    ("yubikey-5-nfc",           "YubiKey 5 NFC security key",        "llaves-seguridad"),
    ("solokey-security-key",    "SoloKey FIDO2 security key",        "llaves-seguridad"),
    ("nitrokey-pro-2",          "Nitrokey Pro 2",                    "llaves-seguridad"),
    ("nitrokey-storage-2",      "Nitrokey Storage 2",                "llaves-seguridad"),
    ("hardware-password-manager", "hardware password manager device", "llaves-seguridad"),

    ("faraday-bag",             "Faraday bag signal blocking",       "privacidad"),
    ("faraday-box",             "Faraday box RF shielding",          "privacidad"),
    ("usb-data-blocker",        "USB data blocker juice jacking",    "privacidad"),
    ("secure-charging-cable",   "secure charging cable no data",     "privacidad"),
    ("rf-signal-detector",      "RF signal detector bug detector",   "privacidad"),
    ("hidden-camera-detector",  "hidden camera detector",            "privacidad"),
    ("anti-spy-detector",       "anti spy detector RF camera",       "privacidad"),
    ("laptop-privacy-screen",   "laptop privacy screen filter",      "privacidad"),
    ("webcam-cover-slider",     "webcam cover slider privacy",       "privacidad"),
    ("screen-crab",             "Hak5 Screen Crab HDMI",             "privacidad"),

    ("encrypted-usb-drive",     "encrypted USB drive IronKey",       "almacenamiento"),
    ("usb-power-monitor",       "USB power monitor voltage",         "almacenamiento"),
    ("portable-secure-power-bank", "secure power bank portable",     "almacenamiento"),
    ("usb-protocol-analyzer",   "USB protocol analyzer hardware",    "almacenamiento"),
    ("multiport-usb-data-switch", "USB data switch multiport",       "almacenamiento"),

    ("logic-analyzer-usb",      "USB logic analyzer Saleae",         "hardware-hacking"),
    ("jtag-debugger",           "JTAG debugger hardware",            "hardware-hacking"),
    ("eeprom-programmer",       "EEPROM programmer chip",            "hardware-hacking"),
    ("bios-flash-programmer-ch341a", "CH341A BIOS flash programmer", "hardware-hacking"),
    ("esp8266-nodemcu",         "ESP8266 NodeMCU development board", "hardware-hacking"),
    ("esp32-dev-kit",           "ESP32 development kit board",       "hardware-hacking"),
    ("sim-card-reader-writer",  "SIM card reader writer",            "hardware-hacking"),
    ("ir-blaster-receiver-kit", "IR blaster receiver kit",           "hardware-hacking"),
    ("universal-remote-hacking-device", "universal remote control device", "hardware-hacking"),
    ("thermal-camera-module",   "thermal camera module",             "hardware-hacking"),

    ("raspberry-pi-4-4gb",      "Raspberry Pi 4 4GB",                "mini-computadoras"),
    ("raspberry-pi-5-8gb",      "Raspberry Pi 5 8GB",                "mini-computadoras"),
    ("raspberry-pi-zero-w",     "Raspberry Pi Zero W",               "mini-computadoras"),
    ("beaglebone-black",        "BeagleBone Black",                  "mini-computadoras"),
    ("intel-nuc-mini-pc",       "Intel NUC mini PC",                 "mini-computadoras"),
    ("nvidia-jetson-nano",      "NVIDIA Jetson Nano",                "mini-computadoras"),
    ("usb-armory-mk-ii",        "USB Armory Mk II",                  "mini-computadoras"),
    ("pwnagotchi-kit",          "Pwnagotchi Raspberry Pi kit",       "mini-computadoras"),

    ("hardware-firewall-appliance", "Protectli hardware firewall",   "seguridad-red"),
    ("secure-kvm-switch",       "secure KVM switch",                 "seguridad-red"),

    ("lock-pick-set",           "professional lock pick set",        "seguridad-fisica"),
    ("digital-door-lock-tester", "digital door lock tester",        "seguridad-fisica"),
    ("key-decoder-tool",        "key decoder tool",                  "seguridad-fisica"),

    ("scada-test-device",       "SCADA security testing device",     "iot-scada"),
    ("iot-security-testing-kit", "IoT security testing kit",         "iot-scada"),
    ("smart-home-pentest-kit",  "smart home pentest kit",            "iot-scada"),
]


# ─── FUNCIÓN: buscar imagen en Amazon ────────────────────────────────────────
def buscar_imagen_amazon(query):
    url = f"https://www.amazon.com/s?k={requests.utils.quote(query)}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar primera imagen de resultado
        img_tags = soup.select("img.s-image")
        if img_tags:
            return img_tags[0].get("src")

        # Fallback: buscar cualquier imagen de producto
        img_tags = soup.find_all("img", {"data-image-latency": "s-product-image"})
        if img_tags:
            return img_tags[0].get("src")

    except Exception as e:
        print(f"  [!] Error buscando en Amazon: {e}")
    return None


# ─── FUNCIÓN: descargar imagen ───────────────────────────────────────────────
def descargar_imagen(url_img, ruta_destino):
    try:
        r = requests.get(url_img, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            with open(ruta_destino, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  [!] Error descargando imagen: {e}")
    return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    base_dir = "imagenes"
    os.makedirs(base_dir, exist_ok=True)

    total = len(PRODUCTOS)
    exito = 0
    fallidos = []

    print(f"\n{'='*55}")
    print(f"  Descargador de imágenes - ViNEK Cybersecurity")
    print(f"  Total de productos: {total}")
    print(f"{'='*55}\n")

    for i, (slug, query, categoria) in enumerate(PRODUCTOS, 1):
        carpeta = os.path.join(base_dir, categoria)
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"{slug}.jpg")

        # Si ya existe, skip
        if os.path.exists(ruta):
            print(f"[{i}/{total}] ⏭  Ya existe: {slug}")
            exito += 1
            continue

        print(f"[{i}/{total}] 🔍 Buscando: {query}")
        url_img = buscar_imagen_amazon(query)

        if url_img:
            ok = descargar_imagen(url_img, ruta)
            if ok:
                print(f"         ✅ Guardado: {categoria}/{slug}.jpg")
                exito += 1
            else:
                print(f"         ❌ No se pudo descargar la imagen")
                fallidos.append(slug)
        else:
            print(f"         ❌ No se encontró imagen en Amazon")
            fallidos.append(slug)

        # Pausa aleatoria para no ser bloqueado por Amazon
        time.sleep(random.uniform(2.5, 5.0))

    print(f"\n{'='*55}")
    print(f"  Completado: {exito}/{total} imágenes descargadas")
    if fallidos:
        print(f"\n  Fallidos ({len(fallidos)}):")
        for slug in fallidos:
            print(f"    - {slug}")
    print(f"{'='*55}\n")

    if fallidos:
        print("Tip: Para los fallidos, búscalos manualmente en:")
        print("  https://www.amazon.com o https://www.aliexpress.com\n")


if __name__ == "__main__":
    main()