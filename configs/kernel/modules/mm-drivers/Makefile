# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
mm_drivers_root := $(abspath $(KERNEL_SRC)/../houji-modules/mm-drivers)
mm_drivers := hw_fence sync_fence msm_ext_display

.PHONY: modules modules_install
modules modules_install:
	+set -e; for module in $(mm_drivers); do \
	    $(MAKE) -C $(KERNEL_SRC) M=$(mm_drivers_root)/$$module \
	        MSM_HW_FENCE_ROOT=$(mm_drivers_root)/ \
	        SYNC_FENCE_ROOT=$(mm_drivers_root)/ \
	        MSM_EXT_DISPLAY_ROOT=$(mm_drivers_root)/ \
	        CONFIG_ARCH_PINEAPPLE=y $@; \
	done
