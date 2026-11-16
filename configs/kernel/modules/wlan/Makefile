# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
wlan_root := $(abspath $(KERNEL_SRC)/../houji-modules/wlan)
dataipa_root := $(abspath $(KERNEL_SRC)/../houji-modules/dataipa)
override M := $(wlan_root)/qcacld-3.0

# The MiCode profile targets Kiwi v2 on the Android Common Kernel.
# Legacy Kbuild calls the profile's WIFI_MONITOR_SUPPORT_Y_WLAN_TX_MON_2_0
# selection WLAN_TX_MON_2_0; keep its TX monitor implementation enabled.
wlan_options := WLAN_ROOT=$(M) WLAN_COMMON_ROOT=cmn WLAN_COMMON_INC=$(M)/cmn \
    WLAN_FW_API=$(wlan_root)/fw-api WLAN_PLATFORM_INC=$(wlan_root)/platform/inc \
    DATA_IPA_INC=$(dataipa_root)/drivers/platform/msm/include \
    CONFIG_IPA_OUT_OF_TREE=y CONFIG_CNSS_OUT_OF_TREE=y CONFIG_WLAN_TX_MON_2_0=y \
    CONFIG_QCA_CLD_WLAN=m CONFIG_QCA_WIFI_ISOC=0 CONFIG_QCA_WIFI_2_0=1 \
    CONFIG_QCA_CLD_WLAN_PROFILE=pineapple_gki_kiwi-v2 MODNAME=qca_cld3_kiwi_v2 \
    DEVNAME=wlan DYNAMIC_SINGLE_CHIP=kiwi_v2

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) $(wlan_options) \
	    KBUILD_EXTRA_SYMBOLS="$(dataipa_root)/Module.symvers $(wlan_root)/platform/Module.symvers" \
	    KCFLAGS="$(KCFLAGS) -D__ANDROID_COMMON_KERNEL__ -DCONFIG_IPA_WDI_UNIFIED_API=1" $@
