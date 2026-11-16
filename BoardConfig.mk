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

# Kernel: use a matched stock bundle until source driver bring-up is complete.
include $(DEVICE_PATH)/configs/kernel/mode.mk
ifeq ($(HOUJI_BUILD_KERNEL_FROM_SOURCE),true)
include $(DEVICE_PATH)/configs/kernel/source.mk
else
include $(DEVICE_PATH)/configs/kernel/prebuilt.mk
endif

# OTA
TARGET_OTA_ASSERT_DEVICE := houji,houjiin

# Properties
TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop

# SEPolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Inherit from the proprietary version
include vendor/xiaomi/houji/BoardConfigVendor.mk
