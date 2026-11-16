# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
rmnet_core_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet/core)
rmnet_mem_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet-ext/mem)
dataipa_root := $(abspath $(KERNEL_SRC)/../houji-modules/dataipa)
override M := $(rmnet_core_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) \
	    KBUILD_EXTRA_SYMBOLS="$(dataipa_root)/Module.symvers $(rmnet_mem_root)/Module.symvers" \
	    KCFLAGS="$(KCFLAGS) -DCONFIG_RMNET_LA_PLATFORM=1 \
	        -DRMNET_TRACE_INCLUDE_PATH=$(rmnet_core_root) \
	        -I$(rmnet_mem_root) -I$(dataipa_root)/drivers/platform/msm/include \
	        -I$(dataipa_root)/drivers/platform/msm/include/uapi" $@
