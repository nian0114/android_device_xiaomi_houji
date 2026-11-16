# Source kernel with selected stock modules

The kernel Image and existing source drivers remain source-built. Six selected
modules currently use unmodified originals from global OS3.0.305.0.WNCMIXM:

| Module | Reason | Original partition |
| --- | --- | --- |
| miev.ko | Original boot load-list entry and Xiaomi event transport used by stock modules | vendor_boot ramdisk |
| nxp-nci.ko | Active qcom,sn-nci hardware node | vendor_dlkm |
| spcom.ko | Active qcom,spcom secure processor communication node | vendor_dlkm |
| spss_utils.ko | Active qcom,spss-utils firmware/control node | vendor_dlkm |
| btpower.ko | Stock qcom,kiwi Bluetooth power node | vendor_dlkm (late group) |
| bt_fm_slim.ko | Stock slim217,221 Bluetooth audio endpoint | vendor_dlkm (late group) |

The blobs, exact ROM archive name, partition provenance and SHA-256 hashes
are versioned in vendor/xiaomi/houji/kernel/OS3.0.305.0.WNCMIXM/.
This directory is intentionally separate from generated vendor extraction
makefiles: the stock external-module adapter owns staging and dependency checks.
When updating the ROM baseline, re-extract these selected files from the recorded
partitions and review/update the manifest and adapter together.

## Build integration

The bootstrap stock adapter runs before other external modules through the existing
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

In the initial check against 6.1.25-g7cbc6862bbca, both selected modules
have all imports available
with identical CRCs, including module_layout. Installing them alongside the
374 source modules passes depmod -e -F System.map with no unresolved symbols.
The adapter also rejects the actual stock Synaptics module on unavailable
Xiaomi interfaces rather than silently installing it.

The integrated check against 6.1.25-g23e4425353c8 also passes both stock
modules' imports and original hashes. The complete staging directory has
382 source modules plus these two files, and depmod reports no unresolved
symbols. This is still a build-time result; packaging and device behavior
remain unverified.

A broader initial scan of the 105 missing names found 45 with no missing
versioned import or CRC conflict against current source exports. Eight have
CRC conflicts and 58 have unavailable versioned imports; those groups overlap.
These figures are candidates for further investigation, not a decision to
ship all 45 modules. The temporary report is out/houji-prebuilt-audit/stock-vs-source.json.

CRC checks do not prove that every structure layout, behavior, CFI callback,
hardware state or firmware interaction is compatible. Actual device loading,
event transport and NFC functionality remain unverified. Preserve enforcement
and inspect runtime errors during bringup; prefer matching source when available.

## Source event consumers

The current qcom-hv-haptics source includes xm-haptic.h, but its event API
calls are guarded by CONFIG_MIEV. That option is not enabled in this source
configuration, and the installed haptics module does not import cdev_tevent_*
or depend on miev. The older MiCode display source does not call this API.

An initial attempt to bridge the core API was withdrawn after checking the
actual linked module. Core modpost does not receive stock event exports.
The original MiCode event header is retained; its disabled no-op definitions
are not evidence of a working source event implementation.

The saved original export table is still verified against the miev ELF by
the stock adapter and is available for future validated external consumers.
Before enabling an event consumer, establish a compatible public API and
CFI/structure behavior. The stock module's split BTF could not be resolved
with the newer stock boot kernel's base BTF, so static CRC checks alone
do not establish this interface ABI. Runtime validation is still required.

## SPSS fallback selection

spcom.ko and spss_utils.ko come from the same existing MIXM vendor_dlkm dump.
No additional ROM extraction is needed. Both pass the existing production
verifier against 6.1.25-gafccd6677c77 using the core source Module.symvers:
original hashes, AArch64 ELF, vermagic flags, all imported CRCs including
module_layout, strong imports and duplicate-export checks. Neither adds an
export, so the saved five miev export CRCs remain unchanged.

The actual qcom,spcom and qcom,spss-utils nodes are active in both product DTs
and all four stock merged DTs. Their 26 properties per tree match after
normalizing remoteproc/reserved-memory references, including channel names,
register addresses, fuse bits and firmware names. Their real source providers
are qcom_ipc_logging, qcom_spss and rproc_qcom_common. Production installation
and complete-staging depmod are recorded in bringup.md. Device loading, SPSS
firmware and userspace communication remain unverified.

A new read-only screen against that release examined the previous 92 missing
original modules, using core plus actually installed module exports. Forty
passed the preliminary link screen; this does not select all forty for
shipping. Some other blobs have genuine CRC conflicts: xiaomi_touch's
panel_event_notifier_register differs, while synaptics_tcm2 has Gunyah CRC
conflicts and unavailable Xiaomi touch interfaces. More vendor extraction
would not fix those interface differences. The temporary current screen is
out/houji-stock-candidates-current.json.

The stock adapter runs before external source drivers, so each newly selected
blob must still pass its production inputs at that point in the build. A
broader screen including later source modules is only a candidate search,
not a substitute for that check or runtime validation.

## Late group and ordered provider validation

The original four-module bootstrap group stays first because the display
build reads its genuine miev export table. A separate stock-extra adapter
runs after all source adapters. Its manifest is
vendor/xiaomi/houji/kernel/OS3.0.305.0.WNCMIXM/extra/modules.json.
It passes only the actual bootstrap and securemsm symbol tables in addition
to the current core table. Providers therefore exist from this build before
late consumers are checked; no old installed module tree is used as input.

The verifier adds an original module's exports to its provider map only after
that module's own imports, flags and bytes pass validation. Manifests must
list providers before consumers. A missing provider, consumer-first order,
self-dependency or cycle cannot satisfy imports. Duplicate exports and module
entries are rejected. Each group retains a separately checked original export
table and stages to its own directory; the bootstrap group remains unchanged.

The Bluetooth late group orders btpower before bt_fm_slim. btpower uses the
source-built securemsm provider; bt_fm_slim uses btpower and bootstrap miev.
Hash, architecture, vermagic, full CRC and strong-import checks stay enabled.
Bluetooth/SLIM DT descriptions are restored from the same actual MIXM merged
trees, rather than guessing another phone's supplies or GPIOs. Production
installation, DT checks and remaining runtime limits are recorded in bringup.md.
