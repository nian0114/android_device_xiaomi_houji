# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
display_root := $(abspath $(KERNEL_SRC)/../houji-modules/display)
mm_drivers_root := $(abspath $(KERNEL_SRC)/../houji-modules/mm-drivers)
mmrm_root := $(abspath $(KERNEL_SRC)/../houji-modules/mmrm-driver)
securemsm_root := $(abspath $(KERNEL_SRC)/../houji-modules/securemsm-kernel)
android_root := $(abspath $(KERNEL_SRC)/../../..)
kernel_out := $(if $(filter /%,$(O)),$(O),$(android_root)/$(O))
override M := $(display_root)

display_symvers := $(mm_drivers_root)/hw_fence/Module.symvers \
    $(mm_drivers_root)/sync_fence/Module.symvers \
    $(mm_drivers_root)/msm_ext_display/Module.symvers \
    $(mmrm_root)/driver/Module.symvers \
    $(securemsm_root)/Module.symvers \
    $(kernel_out)/houji-stock/Module.symvers

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) DISPLAY_ROOT=$(display_root) \
	    CONFIG_ARCH_PINEAPPLE=y CONFIG_DRM_MSM=m \
	    KBUILD_EXTRA_SYMBOLS="$(display_symvers)" $@
