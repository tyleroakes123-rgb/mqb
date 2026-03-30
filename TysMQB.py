from Crypto.Cipher import AES
import hmac
import hashlib
import re

MASTER_KEY = b'VAG IMMO KEY 123'

def extract_all(input_text):
    # Remove all garbage, spaces, headers, everything
    hexstr = re.sub('[^0-9A-Fa-f]', '', input_text)

    # Auto detect what we got
    if len(hexstr) == 32:
        print("\n✅ Detected CS from dump")
        return bytes.fromhex(hexstr)
    if len(hexstr) == 64:
        print("\n✅ Detected 27 01 Seed")
        aes = AES.new(MASTER_KEY, AES.MODE_ECB)
        seed = bytes.fromhex(hexstr)
        return aes.encrypt(seed[0:16]) + aes.encrypt(seed[16:32])
    if len(hexstr) > 120:
        print("\n✅ Detected full K02 Trace")
        f9 = re.search('02 F9.*((?:[0-9A-F]{2} ?){4})', input_text, re.IGNORECASE)
        fa = re.search('02 FA.*((?:[0-9A-F]{2} ?){4})', input_text, re.IGNORECASE)
        if f9 and fa:
            cs_hex = re.sub('[^0-9A-F]', '', f9.group(1) + fa.group(1))
            return bytes.fromhex(cs_hex)

    raise Exception("Could not find CS, Seed or K02 trace")


def generate_all(cs):
    print(f"\n🔑 Permanent Car CS: {cs.hex().upper()}")

    # Calculate 4 digit PIN
    pin = 0
    for b in cs:
        pin = ((pin << 5) + pin) + b
    pin = pin % 10000
    print(f"\n📍 PIN Code: {pin:04d}")

    # Calculate full syncfile exactly as the telegram guy sends you
    syncfile = hmac.new(MASTER_KEY, cs, hashlib.sha256).digest()
    print(f"\n📄 Full Syncfile: {syncfile.hex().upper()}")

    print("\n\nSync Codes:")
    print("----------------------------------------")
    print(f'{"Counter":<8} {"Sync Code"}')
    print("----------------------------------------")
    for counter in range(0, 11):
        buffer = cs + counter.to_bytes(4, byteorder='big')
        mac = hmac.new(MASTER_KEY, buffer, hashlib.sha256).digest()
        sync_code = mac[0:16].hex(' ').upper()
        if counter == 1:
            prefix = "👉 "
        elif counter == 2:
            prefix = "⚠️  "
        else:
            prefix = "   "
        print(f'{prefix}{counter:<6} {sync_code}')

    print("\n----------------------------------------")
    print("Use Counter 1 first. If car dies after 1s use Counter 2.")


if __name__ == '__main__':
    print('MQB All In One Tool')
    print('Paste K02 Trace, Seed or CS below')
    print('----------------------------------------')
    while True:
        i = input("\nPaste here: ")
        try:
            cs = extract_all(i)
            generate_all(cs)
        except Exception as e:
            print(f"❌ Error: {e}")