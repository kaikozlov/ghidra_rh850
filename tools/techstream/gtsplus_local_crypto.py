"""Decode installed GTS+ packaging locally; never contact application services.

Packaging material is read from the pinned installed implementation, not copied
into source or emitted. Callers own source identity pins and disclosure filtering.
"""
from __future__ import annotations

import hashlib
import io
import struct
import zipfile
from pathlib import Path

import dnfile
import pefile
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import unpad

from tools.techstream.inspect_dotnet_il import type_name


def decrypt_file(path: Path, passphrase_file: Path | bytes, cm_path: Path, *, key_type: int = 2) -> bytes:
    """Mirror CM DoFileDecryption's local file path (no authentication calls)."""
    pe = pefile.PE(str(cm_path))
    # FUN_100021e0: index * 0x68f + 0x101b3149, byte XOR 0x49.
    anchors = {
        0x2321: "8db049311b10",
        0x232C: "80f149",
        0x2D23: "6800040000",
        0x2D34: "e827230100",
        0x13BB18: "ab0100001000000020000000100000000200000001000000",
        0x13D604: "5348413100",
    }
    for rva, expected in anchors.items():
        if pe.get_data(rva, len(expected) // 2).hex() != expected:
            raise ValueError(f"CM packaging implementation drift at RVA {rva:#x}")
    material = bytes(x ^ 0x49 for x in pe.get_data(0x1b3149 + key_type * 0x68f, 0x68f))
    rsa = RSA.import_key(material)
    encrypted = passphrase_file if isinstance(passphrase_file, bytes) else passphrase_file.read_bytes()
    sentinel = object()
    password = PKCS1_v1_5.new(rsa).decrypt(encrypted, sentinel)
    if password is sentinel:
        raise ValueError("invalid packaged passphrase envelope")
    data = path.read_bytes()
    if len(data) < 48 or (len(data) - 32) % 16:
        raise ValueError("invalid CM file envelope")
    # DoFileDecryption 0x10002d23 pushes 0x400 iterations; decompiler's
    # inferred byte parameter truncates this value, so use the instruction.
    key = hashlib.pbkdf2_hmac("sha1", password, data[:16], 1024, dklen=32)
    return unpad(AES.new(key, AES.MODE_CBC, data[16:32]).decrypt(data[32:]), 16)


def embedded_passphrase(resource_path: Path) -> bytes:
    pe = dnfile.dnPE(str(resource_path))
    for resource in pe.net.resources:
        for entry in getattr(resource.data, "entries", []):
            if entry.name == "ppf_tmc":
                return bytes(entry.value)
    raise ValueError("missing ppf_tmc packaging resource")


def asset_mask(crypt_path: Path) -> bytes:
    pe = dnfile.dnPE(str(crypt_path))
    rows = {id(f.row) for t in pe.net.mdtables.TypeDef if type_name(t) == "<PrivateImplementationDetails>" for f in t.FieldList}
    candidates = [r for r in pe.net.mdtables.FieldRva if id(r.Field.row) in rows and str(r.Field.row.Name).startswith("04ABC882")]
    if len(candidates) != 1:
        raise ValueError("GUI asset mask field drift")
    return pe.get_data(candidates[0].Rva, 8)


def decode_gui(path: Path, cm_path: Path, resource_path: Path, crypt_path: Path, certificate: Path) -> dict[str, bytes]:
    """Authenticate the decrypted ZIP and decode each masked frontend asset."""
    password = decrypt_file(path.with_suffix(".cpf"), embedded_passphrase(resource_path), cm_path)
    key = password[:16].ljust(16, b"\0")
    data = path.read_bytes()
    iv_len = struct.unpack_from("<I", data)[0]
    if iv_len != 16:
        raise ValueError("GUI IV length drift")
    plain = unpad(AES.new(key, AES.MODE_CBC, data[4:20]).decrypt(data[20:]), 16)
    signature, archive = plain[:256], plain[256:]
    # GuiFile.Load passes SHA256(zipData) to RSACryptoServiceProvider.VerifyData.
    pkcs1_15.new(RSA.import_key(certificate.read_bytes())).verify(SHA256.new(SHA256.new(archive).digest()), signature)
    mask = asset_mask(crypt_path)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        return {item.filename: bytes(x ^ mask[i % len(mask)] for i, x in enumerate(zf.read(item))) for item in zf.infolist() if not item.is_dir()}
