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

模块加载顺序和 blocklist 来自新 ROM，保存在 `configs/kernel/`；system_dlkm 的
原始模块路径已规范化为文件名，以符合 Lineage 模块安装器的匹配方式。
配置不复制旧预编译 Image 或 stock `.ko`，不跳过缺失模块。

当前选用主树已有的 Clang `r547379`。MiCode 原构建配置使用 `r487747c`，
工具链兼容性仍需在源码完整后实际编译确认，必要时切换原版工具链。

## 已知源码阻塞

**当前不是可刷机版本，源码内核尚未编译成功。**

官方发布的 `drivers/misc/Kconfig` 引用了不存在的
`drivers/misc/hwid/Kconfig`，`CONFIG_MI_HARDWARE_ID` 对应实现也缺失。
配置生成已在此处失败，不能用空文件、假模块或简单删除驱动来视作修复。

`lineage.dependencies` 会下载同分支官方 DTS、相机、WLAN 与显示 DTS，
其中外置源码目前作为移植输入，尚未接入完整模块和 techpack DTS 合并构建。
仍需补全与平台版本匹配的显示、音频、GPU、视频、安全及其他外置模块源码和构建配置。
新 ROM 的模块清单还包含旧源码未必提供的模块；必须补全实现并核对依赖。

6.1.25 源码与新固件的 6.1.157 模块不能仅凭大版本相同认定兼容。
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

目前产品配置解析通过；内核配置在上面的缺失 hwid 源码处失败。
完整 ROM 编译和真机启动尚未验证。
