# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
rmnet_mem_root := $(abspath $(KERNEL_SRC)/../houji-modules/datarmnet-ext/mem)
override M := $(rmnet_mem_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) $@
