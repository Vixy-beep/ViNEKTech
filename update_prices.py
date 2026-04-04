"""
Script para actualizar precios de productos desde tabla CSV
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Product
from decimal import Decimal

# Tabla de precios correctos
PRECIOS = [
    ("acr122u-nfc-reader", Decimal("38.00")),
    ("alfa-awus036ach", Decimal("55.00")),
    ("alfa-awus036nha", Decimal("42.00")),
    ("anti-spy-detector", Decimal("58.00")),
    ("bash-bunny", Decimal("149.00")),
    ("beaglebone-black", Decimal("79.00")),
    ("bios-flash-programmer-ch341a", Decimal("14.00")),
    ("bluetooth-sniffer", Decimal("59.00")),
    ("chameleon-ultra", Decimal("189.00")),
    ("deauther-watch", Decimal("55.00")),
    ("digispark-usb", Decimal("12.00")),
    ("digital-door-lock-tester", Decimal("145.00")),
    ("drone-signal-analyzer", Decimal("155.00")),
    ("dstike-deauther-oled", Decimal("36.00")),
    ("eeprom-programmer", Decimal("32.00")),
    ("encrypted-usb-drive", Decimal("60.00")),
    ("esp32-dev-kit", Decimal("14.00")),
    ("esp8266-nodemcu", Decimal("10.00")),
    ("faraday-bag", Decimal("25.00")),
    ("faraday-box", Decimal("65.00")),
    ("flipper-zero", Decimal("249.00")),  # Aumentado para mejor margen
    ("glinet-travel-router", Decimal("69.00")),
    ("hackrf-one", Decimal("349.00")),
    ("hardware-firewall-appliance", Decimal("249.00")),
    ("hardware-password-manager", Decimal("52.00")),
    ("hidden-camera-detector", Decimal("42.00")),
    ("industrial-network-sniffer", Decimal("529.00")),
    ("intel-nuc-mini-pc", Decimal("295.00")),
    ("iot-security-testing-kit", Decimal("449.00")),
    ("ir-blaster-receiver-kit", Decimal("18.00")),
    ("jtag-debugger", Decimal("52.00")),
    ("key-croc", Decimal("129.00")),
    ("key-decoder-tool", Decimal("79.00")),
    ("keystroke-injector-usb", Decimal("28.00")),
    ("lan-turtle", Decimal("99.00")),
    ("laptop-privacy-screen", Decimal("30.00")),
    ("lock-pick-set", Decimal("55.00")),
    ("logic-analyzer-usb", Decimal("42.00")),
    ("lora-dev-board", Decimal("24.00")),
    ("malduino", Decimal("35.00")),
    ("multiport-usb-data-switch", Decimal("34.00")),
    ("network-packet-analyzer-device", Decimal("199.00")),
    ("network-tap-hardware", Decimal("62.00")),
    ("nitrokey-pro-2", Decimal("89.00")),
    ("nitrokey-storage-2", Decimal("129.00")),
    ("nvidia-jetson-nano", Decimal("179.00")),
    ("openwrt-router", Decimal("99.00")),
    ("packet-squirrel", Decimal("99.00")),
    ("plunder-bug", Decimal("55.00")),
    ("portable-secure-power-bank", Decimal("45.00")),
    ("portable-vpn-router", Decimal("79.00")),
    ("proxmark3-rdv4", Decimal("349.00")),
    ("pwnagotchi-kit", Decimal("99.00")),
    ("raspberry-pi-4-4gb", Decimal("89.00")),
    ("raspberry-pi-5-8gb", Decimal("119.00")),
    ("raspberry-pi-zero-w", Decimal("28.00")),
    ("rf-signal-detector", Decimal("48.00")),
    ("rfid-cloner-kit", Decimal("32.00")),
    ("rtl-sdr-dongle", Decimal("42.00")),
    ("scada-test-device", Decimal("449.00")),
    ("screen-crab", Decimal("189.00")),
    ("secure-charging-cable", Decimal("16.00")),
    ("secure-kvm-switch", Decimal("199.00")),
    ("shark-jack", Decimal("99.00")),
    ("sim-card-reader-writer", Decimal("42.00")),
    ("smart-home-pentest-kit", Decimal("225.00")),
    ("solokey-security-key", Decimal("38.00")),
    ("thermal-camera-module", Decimal("99.00")),
    ("tp-link-wn722n", Decimal("22.00")),
    ("ubertooth-one", Decimal("149.00")),
    ("universal-remote-hacking-device", Decimal("62.00")),
    ("usb-armory-mk-ii", Decimal("199.00")),
    ("usb-data-blocker", Decimal("14.00")),
    ("usb-power-monitor", Decimal("20.00")),
    ("usb-protocol-analyzer", Decimal("109.00")),
    ("usb-rubber-ducky", Decimal("89.00")),
    ("webcam-cover-slider", Decimal("8.00")),
    ("wifi-pineapple", Decimal("289.00")),
    ("yard-stick-one", Decimal("119.00")),
    ("yubikey-5-nfc", Decimal("72.00")),
    ("zigbee-sniffer", Decimal("55.00")),
]

def main():
    print(f"\n{'='*60}")
    print(f"  Actualizador de precios - ViNEK Cybersecurity")
    print(f"{'='*60}\n")
    
    updated = 0
    errors = []
    
    for slug, price_usd in PRECIOS:
        try:
            product = Product.objects.get(slug=slug)
            old_price = product.price
            product.price = price_usd
            product.save()
            print(f"✅ {slug}: ${old_price} USD → ${price_usd} USD")
            updated += 1
        except Product.DoesNotExist:
            errors.append(f"❌ {slug}: No encontrado")
            print(f"❌ {slug}: No encontrado en BD")
        except Exception as e:
            errors.append(f"❌ {slug}: {str(e)}")
            print(f"❌ {slug}: Error - {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"  Resumen: {updated}/{len(PRECIOS)} precios actualizados")
    if errors:
        print(f"\n  Errores ({len(errors)}):")
        for error in errors:
            print(f"    {error}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
