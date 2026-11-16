# Camera and DSP source modules

The camera adapter builds camera.ko and cameralog.ko from the existing MiCode
shennong-u-oss camera source. It selects the supplied Pineapple configuration
and real Synx vendor implementation, MMRM, secure-camera and SMMU proxy APIs.
The upstream build header is generated through its original Makefile target.
Source symbol tables come from mmrm-driver, synx-kernel and securemsm-kernel.

The DSP adapter builds frpc-adsprpc.ko and cdsp-loader.ko from the Qualcomm
Pineapple-capable source pinned in kernel/xiaomi/houji/lineage.dependencies.
It selects the upstream Pineapple profile/header and uses RPMsg transport,
including the source's CONFIG_COMPAT implementation. Provenance is recorded
in kernel/xiaomi/houji/docs/dev/external-modules.md and houji.xml.

Both adapters use Lineage's existing TARGET_KERNEL_EXT_MODULES interface.
No Lineage main-tree modification, stock replacement for these four modules,
warning suppression or missing-module bypass is introduced.

## Local source fixes

Camera fixes preserve diagnostic values with matching types, print output
fence DMA addresses through the kernel DMA-address format, and include the
real WLED interface declaration. The OIS firmware dump checks its table
bounds before indexing and limits appends to remaining buffer capacity.

DSP fixes make FastRPC trace reinclusion independent of a vendor/qcom source
layout, correct diagnostic/minidump argument types, and guard the legacy
Android.mk entry point when Qualcomm DLKM build infrastructure is absent.

Individual camera and DSP compilation, modpost, linking and BTF have passed.
The camera ELF imports actual Synx, MMRM, SMMU proxy and WLED symbols and
declares securemsm module dependencies. Product installation, full depmod
and remaining load-list gaps are recorded in bringup.md.

## Verification limits

These Android 14-era sources are porting inputs for the Android 16 MIXM
vendor baseline. Compilation does not validate HAL ioctl structures, DSP
firmware interactions, camera sensors/OIS, secure camera sessions or hardware operation.
Device loading and hardware operation remain unverified.

Upstream dependency pins do not include unpublished local driver fixes.
Publish camera and DSP port commits to maintained forks and update manifest
and dependency revisions together before relying on a fresh repo sync.

## Camera device-tree integration

The core MiCode DT release had no active camera driver matches in the
product merged trees. kernel/xiaomi/houji-devicetrees now includes the common
Pineapple camera nodes and actual houji sensor descriptions from MiCode
camera-devicetree, pinned in houji.xml and the kernel dependencies. That input
comes from aurora-u-oss because no shennong-u-oss branch exists there; the
integration uses houji files, not aurora sensor wiring.

Full upstream dtbs compilation passes. Both pineapple and pineapple-v2 accept
the houji overlay using fdtoverlay. Each merged tree has 47 active camera,
two FastRPC and one CDSP-loader matches against the built module OF aliases.
For camera's 47 matched node paths, 917 compared properties match the
corresponding stock MIXM variants after provider phandle normalization,
including GPIO tuples, supplies and clock providers/IDs. Cross-version
comparison differs only in the expected IPE clock-rate table. This is a
description comparison; provider behavior, firmware and HAL compatibility
still require runtime validation.

The temporary comparison output is under out/houji-camera-dt-validation;
it is not a committed test fixture. The camera DT header fix and core DT
integration, like driver fixes, must be published to maintained forks before
upstream input pins can reproduce the working checkout.
