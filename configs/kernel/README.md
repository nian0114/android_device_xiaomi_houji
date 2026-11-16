# Kernel packaging metadata

Module load order and blocklist are extracted from Xiaomi 14 Global
`OS3.0.305.0.WNCMIXM` vendor_boot, vendor_dlkm, and system_dlkm.
The stock kernel is `6.1.157-android14-11-g78a0a76cd7b7-ab15497637`.

These lists specify required modules, not permission to reuse stock binaries.
All modules are installed by Lineage source kernel rules; missing modules must fail the build.
The old 6.1.25 source release still needs missing Xiaomi and external drivers.
See `docs/dev/bringup.md` for current source build blockers.
