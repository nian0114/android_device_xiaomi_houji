#
# Copyright (C) 2023 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/xiaomi/houji

# Inherit from sm8650-common
include device/xiaomi/sm8650-common/BoardConfigCommon.mk

# Display
TARGET_SCREEN_DENSITY := 440

# Kernel: build the MiCode release rather than copying a prebuilt Image.
TARGET_KERNEL_SOURCE := kernel/xiaomi/houji
TARGET_KERNEL_VERSION := 6.1
TARGET_KERNEL_CONFIG := \
    gki_defconfig \
    vendor/pineapple_GKI.config \
    vendor/houji_GKI.config
MERGE_ALL_KERNEL_CONFIGS_AT_ONCE := true
TARGET_KERNEL_CLANG_VERSION := r547379
KERNEL_NO_GCC := true
TARGET_KERNEL_ADDITIONAL_FLAGS := LLVM=1 LLVM_IAS=1 DTC_FLAGS=-@

# Dtb/o
TARGET_KERNEL_DTB := dtbs
TARGET_DTB_LIST_WILDCARD := vendor/qcom/pineapple vendor/qcom/pineapple-v2
BOARD_KERNEL_SEPARATED_DTBO := true
BOARD_PREBUILT_DTBOIMAGE := $(PRODUCT_OUT)/dtbo.img
BOARD_DTBO_CFG := $(DEVICE_PATH)/configs/kernel/dtbo.cfg

# Let the kernel build install source-built modules into the DLKM partitions.
BOARD_USES_VENDOR_DLKMIMAGE := true
BOARD_USES_SYSTEM_DLKMIMAGE := true
TARGET_AUTO_COLLECT_KERNEL_MODULE_DEPS := true
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD := $(strip $(shell cat $(DEVICE_PATH)/configs/kernel/modules.load.boot))
BOARD_RECOVERY_KERNEL_MODULES_LOAD := $(strip $(shell cat $(DEVICE_PATH)/configs/kernel/modules.load.recovery))
BOARD_VENDOR_KERNEL_MODULES_LOAD := $(strip $(shell cat $(DEVICE_PATH)/configs/kernel/modules.load.vendor))
BOARD_SYSTEM_KERNEL_MODULES_LOAD := $(strip $(shell cat $(DEVICE_PATH)/configs/kernel/modules.load.system))
BOARD_VENDOR_RAMDISK_KERNEL_MODULES_BLOCKLIST_FILE := $(DEVICE_PATH)/configs/kernel/modules.blocklist
BOOT_KERNEL_MODULES := $(BOARD_VENDOR_RAMDISK_KERNEL_MODULES_LOAD)
RECOVERY_KERNEL_MODULES := $(BOARD_RECOVERY_KERNEL_MODULES_LOAD)
SYSTEM_KERNEL_MODULES := $(BOARD_SYSTEM_KERNEL_MODULES_LOAD)

# OTA
TARGET_OTA_ASSERT_DEVICE := houji,houjiin

# Properties
TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop

# SEPolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Inherit from the proprietary version
include vendor/xiaomi/houji/BoardConfigVendor.mk
