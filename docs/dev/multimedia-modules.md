# Multimedia module source integration

The source-kernel external module sequence now includes:

1. stock: verify the original MIXM miev/NFC files and real event export CRCs.
2. Existing securemsm, WLAN, IPA and RMNET adapters.
3. mmrm: the actual msm-mmrm clock/resource manager.
4. mm-drivers: hardware fence, software sync fence and external display.
5. synx: Synx and IPCLite from the Qualcomm source repository.
6. display: the original MiCode shennong msm_drm implementation.

The adapters reside in configs/kernel/modules and use Lineage's existing
external-module interface. No Lineage build-system changes are needed.
The three added source repositories guard their legacy Android.mk entry
points on the presence of Qualcomm DLKM infrastructure; Lineage otherwise
uses the adapters and owns module installation.
MMRM builds only its driver directory. Synx currently follows its upstream
Kbuild, including compilation of ipclite_test; the test remains blocked and
is absent from the required load lists.

Display uses real HDCP, MMRM, hardware/sync fence and external-display symbol
tables. The stock adapter also exposes original miev CRCs for source consumers.
No empty symbol tables, forced-load flags, fabricated exports or warning
suppression are introduced. Strict compiler diagnostics remain enabled.

Source provenance and upstream pins are recorded in
kernel/xiaomi/houji/docs/dev/external-modules.md and lineage.dependencies.
The local manifest in houji.xml defines the mirror remote and projects.
Pins identify upstream inputs. Local driver fixes remain unpublished port
commits and must be pushed to maintained forks, with pins updated, for a
fresh checkout to reproduce the patched builds.

The individual source drivers and the integrated product build pass source
compilation, modpost, linking, BTF and module installation. The current
release stages 382 source modules plus two original stock files, with no
duplicate module names and no unresolved imports in the complete staging
directory depmod check. Packaging still fails on 96 unique required names.
Full product staging and missing-module results are recorded in bringup.md.
Neither static ABI checks nor source compilation constitute device validation:
the Android 16 MIXM HAL/firmware interfaces may differ from these Android 14
driver baselines. Boot, display, fence, haptics and NFC behavior remain unverified.
