#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
#
"""Extract a matched stock kernel bundle from an expanded houji fastboot ROM."""

import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

TOP = Path(__file__).resolve().parents[3]
os.environ["PATH"] = str(TOP / "prebuilts/kernel-build-tools/linux-x86/bin") + os.pathsep + os.environ["PATH"]
sys.path.insert(0, str(TOP / "tools/extract-utils"))
from extract_utils.extract_recovery import extract_ramdisk, unpack_bootimg

ROM_VERSION = "OS3.0.307.0.WNCCNXM"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_modules(root):
    modules = list(root.rglob("*.ko"))
    if not modules:
        raise ValueError(f"No modules in {root}")
    for path in modules:
        header = path.read_bytes()[:20]
        if header[:5] != b"\x7fELF\x02" or header[18:20] != b"\xb7\x00":
            raise ValueError(f"Not an AArch64 ELF module: {path}")
    for load_file in root.rglob("modules.load*"):
        for name in load_file.read_text().split():
            if not (load_file.parent / name).is_file():
                raise ValueError(f"{load_file}: missing {name}")
    return len(modules)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", type=Path, help="Expanded images directory, including vendor_dlkm and system_dlkm")
    args = parser.parse_args()
    images = args.images.resolve()
    # Fail before replacing the maintained bundle if the supplied dump is wrong.
    prop_files = list((images / "vendor").rglob("build.prop"))
    if not any(f"ro.vendor.build.version.incremental={ROM_VERSION}" in p.read_text() for p in prop_files):
        raise ValueError(f"Expected the {ROM_VERSION} vendor dump")
    inputs = {name: images / f"{name}.img" for name in ("boot", "vendor_boot", "dtbo")}
    input_hashes = {name: sha256(path) for name, path in inputs.items()}
    output = TOP / "vendor/xiaomi/houji/kernel/stock"
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="houji-kernel-", dir=output.parent) as tmp:
        work = Path(tmp)
        bundle = work / "bundle"
        bundle.mkdir()
        unpack_bootimg(str(inputs["boot"]), str(work / "boot"))
        unpack_bootimg(str(inputs["vendor_boot"]), str(work / "vendor_boot"))
        ramdisks = sorted((work / "vendor_boot").glob("vendor_ramdisk[0-9]*"))
        if len(ramdisks) != 1:
            raise ValueError("Expected the single platform ramdisk from this ROM")
        extract_ramdisk(ramdisks[0], work / "ramdisk")
        shutil.copy2(work / "boot/kernel", bundle / "Image")
        dtb = (work / "vendor_boot/dtb").read_bytes()
        offset = 0
        dtb_count = 0
        while offset < len(dtb):
            magic, size = struct.unpack_from(">II", dtb, offset)
            if magic != 0xD00DFEED or size < 40 or offset + size > len(dtb):
                raise ValueError(f"Invalid concatenated DTB at {offset}")
            offset += size
            dtb_count += 1
        (bundle / "dtb").mkdir()
        (bundle / "dtb/stock.dtb").write_bytes(dtb)
        # Keep the DTBO table and entries, excluding stock padding/AVB footer.
        dtbo = inputs["dtbo"].read_bytes()
        magic, size = struct.unpack_from(">II", dtbo)
        if magic != 0xD7B7AB1E or not 32 <= size <= len(dtbo):
            raise ValueError("Invalid DTBO table")
        (bundle / "dtbo.img").write_bytes(dtbo[:size])
        roots = {
            "vendor_ramdisk": work / "ramdisk/lib/modules",
            "vendor_dlkm": images / "vendor_dlkm/lib/modules",
            "system_dlkm": images / "system_dlkm/lib/modules",
        }
        counts = {}
        for name, root in roots.items():
            counts[name] = validate_modules(root)
            # Preserve paths and metadata, including the versioned system tree.
            shutil.copytree(root, bundle / name / "lib/modules", symlinks=True)
        for required in ("modules.load", "modules.load.recovery", "modules.blocklist"):
            if not (bundle / "vendor_ramdisk/lib/modules" / required).is_file():
                raise ValueError(f"Missing ramdisk {required}")
        release = re.search(rb"Linux version ([^ \x00]+)", (bundle / "Image").read_bytes())
        if release is None:
            raise ValueError("Kernel release string not found")
        provenance = {
            "rom": ROM_VERSION,
            "kernel_release": release[1].decode(),
            "input_sha256": input_hashes,
            "dtb_count": dtb_count,
            "module_counts": counts,
        }
        (bundle / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
        sums = "".join(f"{sha256(p)}  {p.relative_to(bundle)}\n"
                       for p in sorted(bundle.rglob("*")) if p.is_file())
        (bundle / "SHA256SUMS").write_text(sums)
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(bundle), output)
        print(json.dumps(provenance, indent=2))
        print(f"Extracted {output}")


if __name__ == "__main__":
    main()
