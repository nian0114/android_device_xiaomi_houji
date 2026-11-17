
#
# Copyright (C) 2023 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from sm8650-common
$(call inherit-product, device/xiaomi/sm8650-common/common.mk)

# Get non-open-source specific aspects
$(call inherit-product, vendor/xiaomi/houji/houji-vendor.mk)

# Vibrator: only expose primitives backed by device waveform files.
$(call soong_config_set,qti_vibrator,effect_lib,//device/xiaomi/houji:libqtivibratoreffect.houji)

# Euicc
PRODUCT_PACKAGES += \
    XiaomiEuicc \
    XiaomiEsimSwitcher

PRODUCT_BROKEN_VERIFY_USES_LIBRARIES := true

# init
PRODUCT_COPY_FILES += \
    $(LOCAL_PATH)/init/init.houji.rc:$(TARGET_COPY_OUT_VENDOR)/etc/init/init.houji.rc \

# Soong namespaces
PRODUCT_SOONG_NAMESPACES += \
    $(LOCAL_PATH)

# Overlays
PRODUCT_PACKAGES += \
    FrameworksResHouji \
    HoujiEuiccOverlay \
    SettingsOverlayHouji \
    SystemUIResHouji

# Keep stock DLKM paths and dependency metadata for the vendor loading scripts.
include device/xiaomi/houji/configs/kernel/mode.mk
ifneq ($(HOUJI_BUILD_KERNEL_FROM_SOURCE),true)
$(call inherit-product, device/xiaomi/houji/configs/kernel/prebuilt-product.mk)
endif
