# SPDX-License-Identifier: Apache-2.0
.DEFAULT_GOAL := modules
android_root := $(abspath $(KERNEL_SRC)/../../..)
kernel_out := $(if $(filter /%,$(O)),$(O),$(android_root)/$(O))
stock_install_root := $(if $(filter /%,$(INSTALL_MOD_PATH)),$(INSTALL_MOD_PATH),$(android_root)/$(INSTALL_MOD_PATH))
stock_manifest := $(android_root)/vendor/xiaomi/houji/kernel/OS3.0.305.0.WNCMIXM/modules.json
stock_verifier := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))/verify-install.py
stock_depmod := $(android_root)/prebuilts/kernel-build-tools/linux-x86/bin/depmod

.PHONY: modules modules_install
modules modules_install:
	python3 $(stock_verifier) --manifest $(stock_manifest) --kernel-out $(kernel_out) \
	    $(if $(filter modules_install,$@),--install-root $(stock_install_root))
	$(if $(filter modules_install,$@),$(stock_depmod) -b $(stock_install_root) $(shell cat $(kernel_out)/include/config/kernel.release),:)
