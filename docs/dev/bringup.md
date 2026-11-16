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
Image 保持源码编译；仅对逐项验证的原厂模块启用受控回退，见
[预编译模块接入](prebuilt-modules.md)。缺失模块检查保持启用。

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
显示、同步、相机和 FastRPC/CDSP 驱动链已接入源码构建；仍需补全与平台版本匹配的
音频、GPU、视频、触控、SPSS 等外置模块源码和构建配置。
新 ROM 的模块清单还包含旧源码未必提供的模块；必须补全实现并核对依赖。

当前源码为 6.1.25；新固件 system 模块标记为 6.1.157，抽查 vendor 模块标记为 6.1.68。
不能仅凭版本号认定 KMI 兼容或不兼容。
需要完成适当的源码更新/移植、KMI 与符号检查、模块构建及 DT 合并，再进行真机验证。
原厂模块仅在哈希、架构、vermagic 标志和全部导入符号 CRC 检查通过后安装；
目前选择 miev 与 nxp-nci 两项，仍需真机核对实际接口和运行行为。

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

### 网络驱动与适用性核对阶段（2026-11-16，历史快照）

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


### 多媒体源码与受控原厂模块接入（2026-11-16，历史快照）

Image 继续由 MiCode 源码构建；本轮 release 为 `6.1.25-g23e4425353c8`。
新增源码驱动已通过正式产品构建的编译、modpost、链接、BTF 与安装：
msm-mmrm、msm_hw_fence、sync_fence、msm_ext_display、synx-driver、ipclite
和 msm_drm。上游 Kbuild 也会生成 ipclite_test；它仍被 blocklist 屏蔽，
未重新加入要求清单。接入和来源见 [多媒体模块接入](multimedia-modules.md)。

另外安装国际版原始 miev.ko 与 nxp-nci.ko，二者均通过哈希、AArch64 ELF、
vermagic 标志和全部导入 CRC 检查，安装后的 SHA-256 与原厂文件一致。
没有修改它们的 vermagic、CRC 或二进制内容。MIEV 在当前源码配置中未启用，
源码 qcom-hv-haptics 不导入事件 API；不注入无实际消费者的核心链接依赖。
校验边界见 [预编译模块接入](prebuilt-modules.md)。

本 release 的完整暂存目录共有 384 个不同的 .ko：
382 个源码生成、2 个原厂文件；没有重名文件。对完整目录执行
`depmod -e -F System.map` 返回 0，且输出为空。
正式分区打包中仍有 modules.order / modules.builtin 元数据警告；
该完整目录依赖检查不能替代尚未完成的分区打包验证。
Image 为 33,823,232 字节，DTB 已生成。

| 加载清单 | 条目行数 | 去重要求模块数 | 未生成模块数（去重） |
| --- | ---: | ---: | ---: |
| boot | 119 | 119 | 13 |
| recovery | 325 | 324 | 37 |
| system | 59 | 59 | 0 |
| vendor | 359 | 297 | 83 |

全部清单去重后仍缺 96 个名称，比上一阶段的 105 项减少 9 项；
vendor 清单缺口从 91 项减少至 83 项。仍保留的缺口包括音频框架/codec、
GPU、相机、视频、触控、DSP/SPSS 和部分 Xiaomi 扩展。
这些是当前清单与产物的差距，并非已经证明 96 项全部必须保留；
原适用性审计中证据不足的项目还要继续逐项核查。

`m -j24 kernel` 用时 5 分 21 秒，最终因剩余要求模块缺失返回 1；
本轮没有生成产品 dtbo.img。完整 ROM 打包和真机启动、显示、NFC 等功能仍未验证。

日志：out/houji-kernel-multimedia-integrated.log。
当前 release 的缺口、预编译哈希及依赖结果：
out/houji-kernel-multimedia-module-gaps.json。
完整暂存目录 depmod 输出：out/houji-prebuilt-audit/depmod-multimedia.log。
这些生成物和临时审计脚本保留在 out，不提交到工程。

### 相机、DSP 与相机设备树接入（2026-11-16，最新结果）

Image 保持源码编译，当前 release 为 6.1.25-gafccd6677c77。
本阶段新增四个源码模块：camera.ko、cameralog.ko、frpc-adsprpc.ko 和
cdsp-loader.ko，均已在正式 m -j24 kernel 中完成编译、modpost、链接、BTF
和安装。相机使用 MiCode shennong 源码；DSP 使用固定的高通 Pineapple
公开版本。来源、适配和验证边界见 [相机与 DSP 接入](camera-dsp-modules.md)。

分别修复相机诊断参数类型、DMA 地址输出、WLED 接口声明和 OIS 信息输出越界；
DSP 修复 trace 头文件重入路径、诊断类型与缺少 Qualcomm DLKM 环境时的
Android.mk 入口。保留严格编译检查、CFI、modversions 和缺失模块检查。
实际 camera ELF 引用了 Synx、MMRM、SMMU proxy、WLED 接口，并声明
securemsm 模块依赖。FastRPC 包含 CONFIG_COMPAT ioctl 实现与 RPMsg OF alias；
核心的通用 CONFIG_QCOM_FASTRPC 未启用，避免双重绑定。

核对发现原核心源码 DT 中相机活动匹配为 0。现接入 MiCode camera-devicetree
内真实 houji 传感器描述和 Pineapple/v2 公共节点；该仓库无 shennong 分支，
固定使用包含 houji 文件的 aurora-u-oss 输入，不使用 aurora 传感器接线。
完整 dtbs 编译通过，两个产品 DTB 均能应用 houji overlay。
最终合并树各有 47 个相机、2 个 FastRPC 和 1 个 CDSP-loader 活动匹配。
相机的 47 个节点在解析 provider phandle 后，917 项比较属性与对应原厂
DT 版本一致；跨 v1/v2 比较只差预期的 IPE clock-rates 表。
此前删除的 20 个不适用硬件驱动在新源码 DT 上仍无 OF/legacy I2C 匹配；
已 blocklist 的 ipclite_test 未重新加入要求清单。

当前 release 的完整暂存目录共有 388 个不同的 .ko：
386 个源码生成、2 个既有原厂模块；没有重名文件。
完整目录的 depmod -e -F System.map 返回 0，输出为空。
miev 与 nxp-nci 安装文件哈希仍与原始 ROM 一致；MIEV 核心配置仍关闭，
源码 haptics 没有事件 API 导入。本阶段未增加新的预编译回退。
Image 大小为 33,823,232 字节。

| 加载清单 | 条目行数 | 去重要求模块数 | 未生成模块数（去重） |
| --- | ---: | ---: | ---: |
| boot | 119 | 119 | 13 |
| recovery | 325 | 324 | 37 |
| system | 59 | 59 | 0 |
| vendor | 359 | 297 | 79 |

全部清单去重后仍缺 92 个名称，比前一阶段 96 项减少 4 项；
vendor 清单缺口由 83 降至 79。剩余主要为音频框架/codec、GPU、视频、
触控、SPSS 和部分 Xiaomi 扩展。92 是清单与当前产物的差距，不代表
每项已证明为必需；证据不足的项目继续逐项核查，不以跳过检查代替实现。

正式产品命令用时 5 分 32 秒，最终仍因其余清单模块缺失返回 1；
分区打包仍有 modules.order / modules.builtin 元数据警告，未生成产品 dtbo.img。
完整暂存目录依赖通过不等于分区打包完成；尚未完成 ROM 或真机启动、
HAL、传感器/OIS、DSP 固件及其他硬件运行验证。

构建启动时另发现非交互环境 PATH 缺少 /home/nian/bin，roomservice
曾找不到 repo。已安装当前 docs/dev/houji.xml 到本机 local_manifests、
合并 roomservice 重复项目，并在独立配置验证中加入 repo 所在 PATH；
repo manifest 解析及 lunch 均返回 0，无 traceback，也未执行 repo sync。
未修改 Lineage 主树。上游依赖固定版本仍不含本地未推送补丁，需发布到
维护的 fork 并同步更新 revision 后，才能在新 checkout 复现全部修复。

正式构建日志：out/houji-kernel-camera-dsp-integrated.log。
当前 release 缺口、哈希和 ELF 依赖：out/houji-kernel-camera-dsp-module-gaps.json。
完整暂存目录 depmod 输出：out/houji-prebuilt-audit/depmod-camera-dsp.log。
DT 合并与属性比较：out/houji-camera-dt-validation/report.json。
更新后配置检查：out/houji-camera-dsp-lunch.log。
临时脚本和这些验证产物保留在 out，不提交到工程。
