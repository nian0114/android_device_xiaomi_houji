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
firmware interactions, camera sensors/OIS, secure camera sessions or device
tree bindings. Device loading and hardware operation remain unverified.

Upstream dependency pins do not include unpublished local driver fixes.
Publish camera and DSP port commits to maintained forks and update manifest
and dependency revisions together before relying on a fresh repo sync.
