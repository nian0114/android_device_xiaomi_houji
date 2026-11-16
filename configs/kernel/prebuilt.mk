# SPDX-License-Identifier: Apache-2.0

HOUJI_STOCK_KERNEL := vendor/xiaomi/houji/kernel/stock

# Explicitly disable auto-discovery of kernel/xiaomi/houji.
TARGET_KERNEL_SOURCE :=
TARGET_KERNEL_VERSION := 6.1
TARGET_PREBUILT_KERNEL := $(HOUJI_STOCK_KERNEL)/Image
BOARD_PREBUILT_DTBIMAGE_DIR := $(HOUJI_STOCK_KERNEL)/dtb
BOARD_PREBUILT_DTBOIMAGE := $(HOUJI_STOCK_KERNEL)/dtbo.img

BOARD_USES_VENDOR_DLKMIMAGE := true
BOARD_USES_SYSTEM_DLKMIMAGE := true
# Preserve the versioned system module paths expected by the stock init script.
BOARD_SYSTEM_DLKM_SRC := $(HOUJI_STOCK_KERNEL)/system_dlkm

# Signed stock modules must retain their bytes. Android regenerates ramdisk
# dependency metadata; the DLKM trees retain their original metadata and paths.
BOARD_DO_NOT_STRIP_VENDOR_RAMDISK_MODULES := true
BOARD_DO_NOT_STRIP_RECOVERY_MODULES := true
BOARD_VENDOR_RAMDISK_KERNEL_MODULES := $(wildcard $(HOUJI_STOCK_KERNEL)/vendor_ramdisk/lib/modules/*.ko)
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := $(notdir $(shell cat $(HOUJI_STOCK_KERNEL)/vendor_ramdisk/lib/modules/modules.load))
BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD := $(notdir $(shell cat $(HOUJI_STOCK_KERNEL)/vendor_ramdisk/lib/modules/modules.load.recovery))
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_BLOCKLIST_FILE := $(HOUJI_STOCK_KERNEL)/vendor_ramdisk/lib/modules/modules.blocklist
BOARD_RECOVERY_KERNEL_MODULES := $(BOARD_VENDOR_RAMDISK_KERNEL_MODULES)
BOARD_RECOVERY_KERNEL_MODULES_LOAD := $(BOARD_VENDOR_RAMDISK_RECOVERY_KERNEL_MODULES_LOAD)
BOARD_RECOVERY_KERNEL_MODULES_BLOCKLIST_FILE := $(BOARD_VENDOR_RAMDISK_KERNEL_MODULES_BLOCKLIST_FILE)
