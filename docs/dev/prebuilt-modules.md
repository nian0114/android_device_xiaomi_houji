# Source kernel with selected stock modules

The kernel Image and existing drivers remain source-built. Two necessary
modules currently use unmodified originals from global OS3.0.305.0.WNCMIXM:

| Module | Reason | Original partition |
| --- | --- | --- |
| miev.ko | Xiaomi event transport imported by display, GPU and other drivers | vendor_boot ramdisk |
| nxp-nci.ko | Active qcom,sn-nci hardware node | vendor_dlkm |

The blobs, exact ROM archive name, partition provenance and SHA-256 hashes
are versioned in vendor/xiaomi/houji/kernel/OS3.0.305.0.WNCMIXM/.
This directory is intentionally separate from generated vendor extraction
makefiles: the stock external-module adapter owns staging and dependency checks.
When updating the ROM baseline, re-extract these two files from the recorded
partitions and review/update the manifest and adapter together.

## Build integration

The stock adapter runs before other external modules through the existing
TARGET_KERNEL_EXT_MODULES interface. It checks each blob hash, relocatable
AArch64 ELF format, vermagic flags and every imported symbol CRC against the
current source Module.symvers. module_layout is required too.
An undefined strong symbol without a version entry is rejected.
The release token alone is ignored exactly as Linux does when CRCs are present;
other vermagic flags must match a module from the current source build.

The adapter extracts the original exported CRCs and namespaces from the ELF,
writing KERNEL_OBJ/houji-stock/Module.symvers for subsequent source drivers.
These are real stock CRCs, never placeholders. A source driver needing miev
must include that file in KBUILD_EXTRA_SYMBOLS. It also rejects duplicate
exports or a source module with the same filename.

modules_install copies the original bytes into the current release's staging
directory and regenerates depmod metadata. Lineage continues to check the
normal boot/recovery/system/vendor load lists. No main-tree change, forced
module loading, vermagic patch or disabled version/CFI check is used.

## Static verification and limits

Against 6.1.25-g7cbc6862bbca, both selected modules have all imports available
with identical CRCs, including module_layout. Installing them alongside the
374 source modules passes depmod -e -F System.map with no unresolved symbols.
The adapter also rejects the actual stock Synaptics module on unavailable
Xiaomi interfaces rather than silently installing it.

A broader initial scan of the 105 missing names found 45 with no missing
versioned import or CRC conflict against current source exports. Eight have
CRC conflicts and 58 have unavailable versioned imports; those groups overlap.
These figures are candidates for further investigation, not a decision to
ship all 45 modules. The temporary report is out/houji-prebuilt-audit/stock-vs-source.json.

CRC checks do not prove that every structure layout, behavior, CFI callback,
hardware state or firmware interaction is compatible. Actual device loading,
event transport and NFC functionality remain unverified. Preserve enforcement
and inspect runtime errors during bringup; prefer matching source when available.
