# SPDX-License-Identifier: Apache-2.0

# In particular, modules.dep refers to versioned paths in system_dlkm. Copy the
# complete vendor module tree without flattening or regenerating those paths.
PRODUCT_COPY_FILES += $(call find-copy-subdir-files,*,vendor/xiaomi/houji/kernel/stock/vendor_dlkm/lib/modules,$(TARGET_COPY_OUT_VENDOR_DLKM)/lib/modules)
