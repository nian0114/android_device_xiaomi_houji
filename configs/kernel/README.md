# Kernel packaging metadata

The default stock bundle uses CN `OS3.0.307.0.WNCCNXM`: kernel
`6.1.138-android14-11-g0c3d559bcd85-ab14529422`, matched DTB/DTBO,
340 ramdisk, 314 vendor_dlkm and 60 system_dlkm modules. Its original
load metadata is preserved inside `vendor/xiaomi/houji/kernel/stock/`.
See `docs/dev/stock-kernel.md` and `docs/dev/vendor-baseline.md`.

The standalone lists in this directory and controlled prebuilt fallback
wrappers belong to the optional MiCode source development path. They were
audited against Global `OS3.0.305.0.WNCMIXM` and are not used by the default
stock mode. The 6.1.25 source release still needs external driver and KMI
work; missing module checks remain enabled. See `docs/dev/bringup.md`.
