# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
synx_root := $(abspath $(KERNEL_SRC)/../houji-modules/synx-kernel)
mm_drivers_root := $(abspath $(KERNEL_SRC)/../houji-modules/mm-drivers)
override M := $(synx_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) SYNX_ROOT=$(synx_root) \
	    CONFIG_ARCH_PINEAPPLE=y \
	    KBUILD_EXTRA_SYMBOLS=$(mm_drivers_root)/hw_fence/Module.symvers $@
