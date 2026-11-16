# 小米 14 / LineageOS 23.2 开发基线

## 当前基线

- Android 主树、houji、sm8650-common：`lineage-23.2`。
- Vendor：用户提供的国际版 `OS3.0.305.0.WNCMIXM` 完整 Fastboot 包；设备与 common 从同一个 dump 提取，IMS 不再使用旧国行版。
- Vendor 安全补丁：`2026-10-01`。内核安全补丁不据此升级，仍需核查实际源码补丁。
- 内核源码：MiCode `shennong-u-oss`，当前为 `6.1.25`；原始提交 `317e609aa4fb`。
- 固件原有内核：`6.1.157-android14-11-g78a0a76cd7b7-ab15497637`。

## 源码内核接入

`BoardConfig.mk` 使用 `kernel/xiaomi/houji`，依次合并 `gki_defconfig`、
`vendor/pineapple_GKI.config`、`vendor/houji_GKI.config`，通过 Lineage kernel.mk
构建 Image、DTB、DTBO，并把源码模块安装至 vendor ramdisk、recovery、vendor_dlkm 与 system_dlkm。

DTBO 使用 Lineage 默认的 `obj/DTBO_OBJ/arch/arm64/boot/dtbo.img` 中间路径，
再由 Android 镜像规则复制并添加 AVB footer，生成最终的 `$(PRODUCT_OUT)/dtbo.img`。
`BOARD_PREBUILT_DTBOIMAGE` 不能指向最终输出，否则会形成 Ninja 自依赖，
且内核生成规则会覆盖镜像复制和 AVB 签名规则。

模块加载顺序和 blocklist 以新 ROM 为基线，保存在 `configs/kernel/`；system_dlkm 的
原始模块路径已规范化为文件名，以符合 Lineage 模块安装器的匹配方式。

system 清单按高通 houji 的适用性移除了 `gzvm.ko`：它是 MediaTek GenieZone
虚拟机驱动，stock 模块的 OF alias 仅匹配 `mediatek,geniezone-hyp`，本设备 DTS
没有该节点，stock system/vendor 模块依赖表也没有其他模块依赖它。Android 官方
`android14-6.1` 的 `drivers/virt/geniezone/Kconfig` 同样明确说明该 hypervisor
仅支持 MediaTek SoC。此项不是 houji 的 Qualcomm Gunyah 虚拟化驱动。
`wwan.ko` 则通过源码配置 `CONFIG_WWAN=m` 正常构建，模块缺失检查保持启用。
调整后的 system 清单共 59 项，产品构建已将其全部安装到 system_dlkm；
vendor 等后续清单仍需按下文所述补齐外置驱动，不能据此认定整个内核打包完成。
配置不复制旧预编译 Image 或 stock `.ko`，不跳过缺失模块。

当前选用主树已有的 Clang `r547379`。MiCode 原构建配置使用 `r487747c`。
已保留 `CONFIG_WERROR=y`、CFI 和模块版本检查，修正原始代码中的类型/格式错误，
完整 `Image modules`、`dtbs` 和 `modules_install` 均已通过。

## 编译结果与后续阻塞

**源码内核已经编译通过；当前仍不是经过验证的可刷机版本。**

官方发布原来缺少的 `drivers/misc/hwid` 已恢复真实实现，并移除了该目录的 Git 忽略规则。
实现有固定的公开来源，按国际版 stock 模块校准 houji 项目号、参数、位域和 sysfs 接口；
来源与接口说明见 `kernel/xiaomi/houji/docs/dev/hwid.md`。
内核配置生成与 `hwid.o` 编译已通过，9 个导出函数名与 stock 模块一致。

原先 WALT、Gunyah、MHI、irqchip、QRTR、音频切换及其他驱动的编译错误已按驱动分别提交修复。
同时单独修复 QRTR 填充失败后的释放后读取、LED 编号误传地址及 MTD 枚举混用问题。
顶层 Makefile 重复定义 DTS 构建规则的问题也已独立修复。

代码提交 `56b6e8d9ecb5` 的完整构建通过 modpost 和 BTF，生成 33,823,232 字节的 `Image`，
模块安装成功，共 335 个源码 `.ko`，包含真正的 AArch64 `hwid.ko` 及其 9 个预期导出接口。
产物位于 `out/houji-kernel-check/`，模块安装目录为 `out/houji-kernel-modules/`。
复现命令、日志与产物信息见 `kernel/xiaomi/houji/docs/dev/build.md`。

完整 `dtbs` 目标通过；`pineapple.dtb`、`pineapple-v2.dtb` 与 houji 专用 DTBO 均可生成，
并已用 `fdtoverlay` 验证 houji overlay 能应用到两个基础 DTB。官方 DTS 仍有 DTC 警告。
最初 standalone 构建与国际版加载清单按文件名对比，有 164 个去重模块名未生成；boot/recovery/system/vendor
各清单分别为 19/61/2/143 个，彼此存在重叠。需要逐项区分内建功能、配置差异和待移植外置驱动，
不能把文件名差距直接视为全部功能缺失，也不能通过跳过缺失检查来宣称打包成功。
本地差距清单为 `out/houji-kernel-module-gaps.json`。

`lineage.dependencies` 会下载同分支官方 DTS、相机、WLAN 与显示 DTS，
WLAN、securemsm、IPA 和 RMNET 已通过 device 内的 wrapper 接入 `TARGET_KERNEL_EXT_MODULES`；
其他外置驱动及 techpack DTS 合并仍在移植。
仍需补全与平台版本匹配的显示、音频、GPU、视频、SPSS 等外置模块源码和构建配置。
新 ROM 的模块清单还包含旧源码未必提供的模块；必须补全实现并核对依赖。

当前源码为 6.1.25；新固件 system 模块标记为 6.1.157，抽查 vendor 模块标记为 6.1.68。
不能仅凭版本号认定 KMI 兼容或不兼容。
需要完成适当的源码更新/移植、KMI 与符号检查、模块构建及 DT 合并，再进行真机验证。
当前不复用新固件模块来掩盖上述问题。

## Vendor 重提取

完整 Fastboot 包先解压至工作目录，保留原始包。使用主树工具展开其 images：

```sh
export PATH="$PWD/prebuilts/kernel-build-tools/linux-x86/bin:$PATH"
export PYTHONPATH=tools/extract-utils
python3 tools/extract-utils/extract.py --keep-images \
  --extra-partitions vendor_dlkm system_dlkm -- /path/to/rom/images
python3 device/xiaomi/houji/extract-files.py --kang /path/to/rom/images
```

脚本会处理 houji 和 common 两个模块；固件清单包含 Fastboot 原文件名到分区镜像名的映射。
除退出码外，应检查提取日志没有 `file not found`、`Some files failed` 或 traceback，
并确认生成两个 vendor makefile。更新时同步提取 vendor_boot 的模块加载元数据。

本基线移除了 ROM 不提供的旧国行相机文件及 Pixel EuiccGoogle APK，
改用本 ROM 的 `xiaomi-modem-common.jar` 支持 XiaomiEsimSwitcher。
保留 Xiaomi eSIM policy/switcher；Google LPA 不再随包提供，eSIM 完整功能需选定兼容 LPA 后验证。

`vendor/xiaomi/houji/radio/*.img` 使用 Git LFS，其他 vendor 文件正常提交。
需要安装 Git LFS 并执行 `git lfs install`，推送时确保 LFS 对象一并上传。

## 检查与构建

不添加单元测试。先做产品配置解析、内核配置/编译检查，再尝试完整构建：

```sh
source build/envsetup.sh
lunch lineage_houji-bp4a-userdebug
m kernel
# 完成内核与外置模块移植后再执行：
m bacon
```

目前产品配置解析、内核配置生成、完整 Image/modules、dtbs 和模块安装均通过。
Lineage 产品内核打包仍被缺失模块阻塞；完整 ROM 编译和真机启动尚未通过，仍需解决模块与 vendor 接口差异。

## WLAN、IPA 与 RMNET 外部模块接入

所有构建适配位于 `configs/kernel/modules/`，使用 Lineage 已有的外部模块接口，
无需修改 `vendor/lineage/build/tasks/kernel.mk`。构建顺序为：

1. `securemsm`：安全调用、加密、HDCP、随机数和 SMMU proxy 模块。
2. `wlan-platform`：MiCode Pineapple 配置的 CNSS2 与六个 WLAN 公共模块。
3. `rmnet-mem`：IPA 和 RMNET 使用的内存模块。
4. `dataipa`：GSI、IPA、IPANET 与上游配置包含的 IPA 测试模块。
5. `rmnet-core`：蜂窝数据核心和控制模块。
6. `rmnet-ext`：APS、offload、perf、perf_tether、scheduler、SHS 和 WLAN 扩展。
7. `wlan`：MiCode `pineapple_gki_kiwi-v2` profile 的 `qca_cld3_kiwi_v2`。

ICNSS2 暂时保留以匹配 stock 清单，其运行时适用性仍需结合 houji DT 核对。

wrapper 传递真实头文件和上游模块的 `Module.symvers`，不使用空符号表或 stub。
WLAN 启用驱动已有的 Android Common Kernel API 适配，并将 Kleaf profile 的
`WIFI_MONITOR_SUPPORT_Y_WLAN_TX_MON_2_0` 映射到传统 Kbuild 的 `WLAN_TX_MON_2_0`，
保留 TX monitor 实现。FTM 实现漏编、MLO 断连来源字段误用以及严格编译器报告的
诊断类型问题均已在对应驱动仓库分别提交。

新增源码的来源与固定版本见 `kernel/xiaomi/houji/docs/dev/external-modules.md`。
`lineage.dependencies` 与 `docs/dev/houji.xml` 已包含 securemsm、dataipa、
datarmnet 和 datarmnet-ext。manifest 仍固定公开上游输入；本地 porting 分支补丁
尚需发布到维护的 fork 并同步更新 revision，不能认为仅同步上游就包含本地修复。

各 wrapper 的源码编译、modpost、BTF 与 `modules_install` 均已通过。
单独安装验证目录没有安装全部内核基础模块，所产生的 depmod 未解析警告不能作为
完整产品依赖验证；正式产品构建和模块打包结果单独记录在下文。
本轮不增加单元测试，验证使用真实编译、链接和模块安装。

### 产品构建结果（2026-11-16，适用性核对后）

`m -j24 kernel` 已通过 Soong、Kati，完成 Image、DTB、内核模块及上述
全部外置模块的编译和安装；本轮 kernel release 为 `6.1.25-g7cbc6862bbca`。
该 release 的模块暂存目录共 374 个源码 .ko，Wi-Fi、IPA、RMNET、
securemsm 和 CNSS2 均已安装，未出现编译错误。
对完整暂存目录执行 depmod -e -F System.map 通过，退出 0 且无未解析符号输出；
结果保存在 out/houji-module-audit/depmod-after-pruning.log。

本轮在原厂 4 份和源码 2 份 houji 合并 DT、原厂 495 个模块的绑定与依赖元数据、
加载脚本基础上，移除了 21 个不适用的缺失名称：10 个其他高通平台驱动、
10 个替代外设驱动和 1 个明确 blocklist 的测试模块。
不存在保留原厂模块声明依赖这 21 项的情况，调整没有关闭模块缺失检查。
详细名称、证据和保留边界见 [模块适用性审计](module-audit.md)。

产品命令用时 6 分 31 秒，最终仍因保留清单项缺失退出 1。
本轮未生成产品 dtbo.img，不能作为可刷机版本。
仅对当前 release 的暂存目录比较，结果如下；各清单缺失项存在重叠：

| 加载清单 | 条目行数 | 去重要求模块数 | 未生成模块数（去重） |
| --- | ---: | ---: | ---: |
| boot | 119 | 119 | 14 |
| recovery | 325 | 324 | 43 |
| system | 59 | 59 | 0 |
| vendor | 359 | 297 | 91 |

全部清单共有 105 个不同的缺失模块名，由核对前的 126 项减少 21 项。
vendor 缺口由最初 143 项、网络驱动接入后的 107 项降至 91 项。
这里没有批量调整与本轮删除无关的重复行，因此要求模块数需区别行数与去重数。

剩余项按保留依据分为：26 项有 OF alias 活动节点匹配，8 项有专用 compatible
字符串活动节点匹配，30 项有原厂模块反向依赖，1 项仅找到显式用户空间加载，
另外 40 项继续核查。以上分类互斥，不代表这 105 项都已证明必须保留。
显示、相机、音频、GPU、视频、触摸、NFC 等实际驱动仍需继续接入；
不明确的 Xiaomi hook / 调试和自定义总线模块没有仅凭名称删除。

完整构建日志：out/houji-kernel-network-integrated.log。
当前 release 的缺口明细：out/houji-kernel-network-module-gaps.json。
本轮前后对比与临时分析：out/houji-module-audit/。
这些验证产物及临时脚本保留在 out，不提交进源码。
