from Crypto.Cipher import AES
import hmac
import hashlib
import re

MASTER_KEY = b'VAG IMMO KEY 123'

def extract_all(input_text):
    hexstr = re.sub('[^0-9A-Fa-f]', '', input_text)
    found = []

    for match in re.finditer('([0-9A-F]{32})', input_text, re.IGNORECASE):
        found.append(bytes.fromhex(match.group(1)))

    if len(hexstr) == 64:
        print("\n✅ Detected 27 01 Seed")
        aes = AES.new(MASTER_KEY, AES.MODE_ECB)
        seed = bytes.fromhex(hexstr)
        found.append(aes.encrypt(seed[0:16]) + aes.encrypt(seed[16:32]))

    f9 = re.search('02 F9.*((?:[0-9A-F]{2} ?){4})', input_text, re.IGNORECASE)
    fa = re.search('02 FA.*((?:[0-9A-F]{2} ?){4})', input_text, re.IGNORECASE)
    if f9 and fa:
        cs_hex = re.sub('[^0-9A-F]', '', f9.group(1) + fa.group(1))
        found.append(bytes.fromhex(cs_hex))

    if len(found) == 0:
        raise Exception("Could not find CS, Seed or K02 trace")
    
    if len(found) > 1:
        print(f"\n⚠️  Found {len(found)} different CS values")
        print("✅ Cluster is always master, always use the first one listed")

    return list(dict.fromkeys(found))


def generate_all(cs):
    print(f"\n🔑 CS: {cs.hex().upper()}")

    pin = 0
    for b in cs:
        pin = ((pin << 5) + pin) + b
    pin = pin % 10000
    print(f"\n📍 PIN Code: {pin:04d}")

    syncfile = hmac.new(MASTER_KEY, cs, hashlib.sha256).digest()
    print(f"\n📄 Full Syncfile: {syncfile.hex().upper()}")

    print("\n\nSync Codes:")
    print("----------------------------------------")
    print(f'{"Counter":<8} {"Sync Code"}')
    print("----------------------------------------")
    for counter in range(0, 11):
        buffer = counter.to_bytes(4, byteorder='little') + cs
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


if __name__ == '__main__':
    print('Tylers MQB All In One Tool')
    print('Paste K02 Trace, Seed or CS below')
    print('----------------------------------------')
    while True:
        i = input("\nPaste here: ")
        try:
            cs_list = extract_all(i)
            for cs in cs_list:
                generate_all(cs)
            print("\n✅ Use Counter 1 first")
            print("✅ If car runs 1s and dies use Counter 2")
            print("✅ No lockout. You can not brick anything.")
        except Exception as e:
            print(f"❌ Error: {e}")
