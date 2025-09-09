#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import sys
from typing import Optional

try:
    from Crypto.Cipher import ARC4  # from pycryptodome
except Exception:
    print("Missing dependency: pycryptodome. Install with: pip install pycryptodome", file=sys.stderr)
    raise

def _b64_normalize(s: str) -> str:
    s = (s or "").strip().replace(" ", "")
    pad = (-len(s)) % 4
    if pad:
        s += "=" * pad
    return s

def b64decode_auto(s: str) -> bytes:
    s_norm = _b64_normalize(s)
    try:
        return base64.b64decode(s_norm, validate=False)
    except Exception:
        return base64.urlsafe_b64decode(s_norm)

def derive_miot_rc4_key(ssecurity_b64: str, nonce_b64: str) -> bytes:
    ssec = b64decode_auto(ssecurity_b64)
    nonce = b64decode_auto(nonce_b64)
    return hashlib.sha256(ssec + nonce).digest()

def rc4_drop1024_decrypt(key: bytes, ciphertext: bytes) -> bytes:
    cipher = ARC4.new(key, drop=1024)  # RC4 with keystream drop=1024
    return cipher.encrypt(ciphertext)   # RC4 encrypt == decrypt

def pretty_try_json(data: bytes) -> str:
    try:
        txt = data.decode("utf-8")
    except UnicodeDecodeError:
        return f"<{len(data)} bytes (non-UTF8)>\n" + data.hex()
    try:
        return json.dumps(json.loads(txt), ensure_ascii=False, indent=2, sort_keys=True)
    except Exception:
        return txt

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Decrypt MIoT RC4 payloads (header: miot-encrypt-algorithm: ENCRYPT-RC4)")
    p.add_argument("--ssecurity", required=True, help="Base64 ssecurity")
    p.add_argument("--nonce", required=True, help="Base64 _nonce from request")
    p.add_argument("--cipher", help="Base64 response body;")
    p.add_argument("--out", help="Write raw plaintext to file")
    args = p.parse_args(argv)

    cipher_b64: Optional[str] = args.cipher or sys.stdin.read()
    key = derive_miot_rc4_key(args.ssecurity, args.nonce)
    ct = b64decode_auto(cipher_b64)
    pt = rc4_drop1024_decrypt(key, ct)
    pretty = pretty_try_json(pt)

    if args.out:
        with open(args.out, "wb") as f:
            f.write(pt)
        print(f"Wrote plaintext to {args.out}")
    else:
        print(pretty)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
