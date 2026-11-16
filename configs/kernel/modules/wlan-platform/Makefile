# SPDX-License-Identifier: Apache-2.0
# Adapt the official WLAN Kbuild to Lineage's external-module interface.
.DEFAULT_GOAL := modules
WLAN_PLATFORM_ROOT := $(abspath $(KERNEL_SRC)/../houji-modules/wlan/platform)
override M := $(WLAN_PLATFORM_ROOT)

include $(WLAN_PLATFORM_ROOT)/cnss2/pineapple_gki_defconfig
include $(WLAN_PLATFORM_ROOT)/cnss_genl/pineapple_gki_defconfig
include $(WLAN_PLATFORM_ROOT)/cnss_prealloc/pineapple_gki_defconfig
include $(WLAN_PLATFORM_ROOT)/cnss_utils/pineapple_gki_defconfig
# Retain the stock load-list module while its runtime use is audited.
include $(WLAN_PLATFORM_ROOT)/icnss2/pineapple_gki_defconfig

wlan_config_vars := CONFIG_CNSS_OUT_OF_TREE CONFIG_CNSS_GENL \
    CONFIG_CNSS2 CONFIG_CNSS2_QMI CONFIG_BUS_AUTO_SUSPEND \
    CONFIG_CNSS2_SSR_DRIVER_DUMP CONFIG_CNSS_HW_SECURE_DISABLE \
    CONFIG_CNSS2_SMMU_DB_SUPPORT \
    CONFIG_WCNSS_MEM_PRE_ALLOC CONFIG_CNSS_UTILS CONFIG_CNSS_QMI_SVC \
    CONFIG_CNSS_PLAT_IPC_QMI_SVC CONFIG_ICNSS2 CONFIG_ICNSS2_QMI CONFIG_CNSS_QCA6750
wlan_options := WLAN_PLATFORM_ROOT=$(WLAN_PLATFORM_ROOT) \
    KBUILD_EXTRA_SYMBOLS=$(abspath $(KERNEL_SRC)/../houji-modules/securemsm-kernel/Module.symvers) \
    $(foreach config,$(wlan_config_vars),$(config)=$($(config)))

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) $(wlan_options) \
	    KCFLAGS="$(KCFLAGS) -DCONFIG_BUS_AUTO_SUSPEND -DCONFIG_CNSS_QCA6750" $@
