# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
camera_root := $(abspath $(KERNEL_SRC)/../houji-modules/camera)
mmrm_root := $(abspath $(KERNEL_SRC)/../houji-modules/mmrm-driver)
synx_root := $(abspath $(KERNEL_SRC)/../houji-modules/synx-kernel)
securemsm_root := $(abspath $(KERNEL_SRC)/../houji-modules/securemsm-kernel)
override M := $(camera_root)

camera_symvers := $(mmrm_root)/driver/Module.symvers \
    $(synx_root)/Module.symvers \
    $(securemsm_root)/Module.symvers
camera_configs := $(mmrm_root)/config/waipiommrm.conf \
    $(synx_root)/config/pineapplesynx.conf \
    $(securemsm_root)/config/sec-kernel_defconfig_smcinvoke.conf \
    $(securemsm_root)/config/sec-kernel_defconfig_smmu_proxy.conf

.PHONY: modules modules_install camera-header
modules: camera-header

camera-header:
	+$(MAKE) -C $(camera_root) cam_generated_h

modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) \
	    CAMERA_KERNEL_ROOT=$(camera_root) KERNEL_ROOT=$(KERNEL_SRC) \
	    CONFIG_ARCH_PINEAPPLE=y TARGET_SYNX_ENABLE=y \
	    KBUILD_EXTRA_SYMBOLS="$(camera_symvers)" \
	    KBUILD_EXTRA_CONFIGS="$(camera_configs)" $@
