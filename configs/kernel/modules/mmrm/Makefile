# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
mmrm_root := $(abspath $(KERNEL_SRC)/../houji-modules/mmrm-driver)
override M := $(mmrm_root)/driver

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) MMRM_ROOT=$(mmrm_root) \
	    CONFIG_MSM_MMRM=y KCFLAGS="$(KCFLAGS) -include $(mmrm_root)/config/waipiommrmconf.h" $@
