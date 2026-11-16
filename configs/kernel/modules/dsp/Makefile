# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
dsp_root := $(abspath $(KERNEL_SRC)/../houji-modules/dsp-kernel)
override M := $(dsp_root)

.PHONY: modules modules_install
modules modules_install:
	+$(MAKE) -C $(KERNEL_SRC) M=$(M) DSP_ROOT=$(dsp_root) \
	    CONFIG_ARCH_PINEAPPLE=y CONFIG_MSM_ADSPRPC=m \
	    KCFLAGS="$(KCFLAGS) -include $(dsp_root)/config/pineappledspconf.h" $@
