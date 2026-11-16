#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Verify selected stock modules against a source build, then stage originals."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys


class Elf:
    """The Android kernel modules used here are ELF64 little-endian AArch64."""
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        header = struct.unpack_from("<16sHHIQQQIHHHHHH", self.data)
        if header[0][:6] != b"\x7fELF\x02\x01" or header[1:3] != (1, 183):
            raise ValueError(f"{path}: expected relocatable AArch64 ELF64")
        self.sections = [
            struct.unpack_from("<IIQQQQIIQQ", self.data,
                               header[6] + i * header[11])
            for i in range(header[12])
        ]
        names = self.section_data(header[13])
        self.named = {self.cstring(names, s[0]): i
                      for i, s in enumerate(self.sections)}
        self.symbols = {}
        for section in self.sections:
            if section[1] != 2:  # SHT_SYMTAB
                continue
            strings = self.section_data(section[6])
            for offset in range(section[4], section[4] + section[5], section[9]):
                symbol = struct.unpack_from("<IBBHQQ", self.data, offset)
                name = self.cstring(strings, symbol[0])
                if name:
                    self.symbols[name] = symbol

    @staticmethod
    def cstring(data, offset):
        return data[offset:data.index(b"\0", offset)].decode()

    def section_data(self, index):
        section = self.sections[index]
        return self.data[section[4]:section[4] + section[5]]

    def named_data(self, name):
        return self.section_data(self.named[name])

    def symbol_data(self, symbol):
        section = self.sections[symbol[3]]
        offset = section[4] + symbol[4] - section[3]
        end = offset + symbol[5] if symbol[5] else section[4] + section[5]
        return self.data[offset:end]

    def modinfo(self):
        result = {}
        for entry in self.named_data(".modinfo").split(b"\0"):
            if b"=" in entry:
                key, value = entry.decode().split("=", 1)
                result.setdefault(key, []).append(value)
        return result

    def versions(self):
        data = self.named_data("__versions")
        if not data or len(data) % 64:
            raise ValueError(f"{self.path}: invalid or empty symbol versions")
        result = {}
        for offset in range(0, len(data), 64):
            crc = struct.unpack_from("<Q", data, offset)[0]
            result[self.cstring(data, offset + 8)] = crc
        if "module_layout" not in result:
            raise ValueError(f"{self.path}: module_layout CRC missing")
        return result

    def exports(self):
        for name, symbol in self.symbols.items():
            if not name.startswith("__ksymtab_"):
                continue
            exported = name.removeprefix("__ksymtab_")
            crc_symbol = self.symbols["__crc_" + exported]
            crc = struct.unpack_from("<I", self.symbol_data(crc_symbol))[0]
            section_names = [key for key, idx in self.named.items()
                             if idx == symbol[3]]
            kind = ("EXPORT_SYMBOL_GPL" if any("ksymtab_gpl" in key
                                             for key in section_names)
                    else "EXPORT_SYMBOL")
            namespace = self.symbols.get("__kstrtabns_" + exported)
            ns = self.symbol_data(namespace).split(b"\0", 1)[0].decode() if namespace else ""
            yield exported, crc, kind, ns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--kernel-out", required=True, type=Path)
    parser.add_argument("--symvers", action="append", default=[], type=Path)
    parser.add_argument("--install-root", type=Path)
    parser.add_argument("--group", default="houji-stock",
                        choices=("houji-stock", "houji-stock-extra"))
    args = parser.parse_args()
    kernel = args.kernel_out.resolve()
    manifest = json.loads(args.manifest.read_text())
    reference = Elf(kernel / "drivers/misc/hwid/hwid.ko")
    reference_flags = reference.modinfo()["vermagic"][0].split()[1:]
    exports = {}
    for path in [kernel / "Module.symvers", *args.symvers]:
        for line in path.read_text().splitlines():
            fields = line.split()
            crc, name = int(fields[0], 16), fields[1]
            if name in exports and exports[name] != crc:
                raise ValueError(f"conflicting source CRC for {name}")
            exports[name] = crc

    verified = []
    exported = []
    for entry in manifest["modules"]:
        path = args.manifest.parent / entry["file"]
        if path.name != entry["file"] or path.suffix != ".ko":
            raise ValueError("manifest module must be a .ko basename")
        if path in verified:
            raise ValueError(f"{path}: duplicate module in manifest")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"{path}: SHA-256 differs from stock baseline")
        elf = Elf(path)
        flags = elf.modinfo()["vermagic"][0].split()[1:]
        # Linux compares vermagic without release when symbol versions exist.
        if flags != reference_flags:
            raise ValueError(f"{path}: vermagic flags differ: {flags}")
        for name, crc in elf.versions().items():
            if name not in exports:
                raise ValueError(f"{path}: verified providers do not export {name}")
            if exports[name] != crc:
                raise ValueError(f"{path}: CRC differs for {name}: "
                                 f"stock={crc:#x} source={exports[name]:#x}")
        # Refuse strong undefined imports omitted from the version table too.
        versions = elf.versions()
        for name, symbol in elf.symbols.items():
            if symbol[3] == 0 and symbol[1] >> 4 != 2 and name not in versions:
                raise ValueError(f"{path}: unversioned strong import {name}")
        for name, crc, kind, namespace in elf.exports():
            if name in exports:
                raise ValueError(f"{path}: duplicate export {name}")
            exported.append((crc, name, path.stem, kind, namespace))
            # Only an earlier fully checked module may provide a later import.
            # This rejects self-dependencies, cycles and consumer-first order.
            exports[name] = crc
        verified.append(path)

    generated = kernel / args.group
    generated.mkdir(exist_ok=True)
    symvers = "".join(
        f"{crc:#010x}\t{name}\t{provider}\t{kind}\t{namespace}\n"
        for crc, name, provider, kind, namespace in exported
    )
    saved = (args.manifest.parent / "Module.symvers").read_bytes()
    if (hashlib.sha256(saved).hexdigest() != manifest["export_symvers_sha256"]
            or saved != symvers.encode()):
        raise ValueError("saved export CRCs differ from original ELF tables")
    (generated / "Module.symvers").write_text(symvers)
    release = (kernel / "include/config/kernel.release").read_text().strip()
    if args.install_root:
        destination = args.install_root / "lib/modules" / release / "extra" / args.group
        destination.mkdir(parents=True, exist_ok=True)
        for path in verified:
            existing = [p for p in destination.parents[1].rglob(path.name)
                        if p != destination / path.name]
            if existing:
                raise ValueError(f"source already provides {path.name}: {existing}")
            shutil.copyfile(path, destination / path.name)
    print(f"Verified {len(verified)} stock modules against {release}; "
          f"extracted {len(exported)} original export CRCs. Runtime validation pending.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, struct.error) as error:
        sys.exit(f"Stock module compatibility check failed: {error}")
