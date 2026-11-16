# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
securemsm_root := $(abspath $(KERNEL_SRC)/../houji-modules/securemsm-kernel)
override M := $(securemsm_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) SSG_MODULE_ROOT=$(securemsm_root) \
	    KCFLAGS="$(KCFLAGS) -DSMCINVOKE_TRACE_INCLUDE_PATH=$(securemsm_root)/smcinvoke" $@
