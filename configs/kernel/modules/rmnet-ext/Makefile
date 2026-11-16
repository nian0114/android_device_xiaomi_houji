# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
rmnet_ext_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet-ext)
rmnet_core_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet/core)
dataipa_root := $(abspath $(KERNEL_SRC)/../houji-modules/dataipa)
rmnet_ext_modules := aps offload perf perf_tether sch shs wlan

.PHONY: modules modules_install
modules modules_install:
	+set -e; for module in $(rmnet_ext_modules); do \
	    $(MAKE) -C $(KERNEL_SRC) M=$(rmnet_ext_root)/$$module \
	        RMNET_CORE_INC_DIR=$(rmnet_core_root) \
	        KBUILD_EXTRA_SYMBOLS="$(rmnet_core_root)/Module.symvers $(rmnet_ext_root)/mem/Module.symvers $(dataipa_root)/Module.symvers" \
	        KCFLAGS="$(KCFLAGS) -DCONFIG_RMNET_LA_PLATFORM=1 -I$(rmnet_ext_root)/mem" $@; \
	done
