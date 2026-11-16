# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
dataipa_root := $(abspath $(KERNEL_SRC)/../houji-modules/dataipa)
rmnet_mem_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet-ext/mem)
override M := $(dataipa_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) DATAIPA_ROOT=$(dataipa_root) \
	    KBUILD_EXTRA_SYMBOLS=$(rmnet_mem_root)/Module.symvers \
	    KCFLAGS="$(KCFLAGS) -I$(rmnet_mem_root) \
	        -DGSI_TRACE_INCLUDE_PATH=$(dataipa_root)/drivers/platform/msm/gsi \
	        -DIPA_TRACE_INCLUDE_PATH=$(dataipa_root)/drivers/platform/msm/ipa/ipa_v3 \
	        -DRNDIS_TRACE_INCLUDE_PATH=$(dataipa_root)/drivers/platform/msm/ipa/ipa_clients" $@
