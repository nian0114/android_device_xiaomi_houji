# 原厂内核优先的系统 bring-up

## 默认方案

先用国际版 `OS3.0.305.0.WNCMIXM` 的同套内核、DTB、DTBO 和模块构建
LineageOS；MiCode 6.1.25 源码及外置驱动移植保留为可选开发路径。
默认选择在 `configs/kernel/mode.mk`：
`HOUJI_BUILD_KERNEL_FROM_SOURCE ?= false`。要继续源码移植时将该默认值改为
`true`，并使用干净的产品输出，防止旧 .ko 或启动镜像混入。

原厂材料位于 `vendor/xiaomi/houji/kernel/stock/`：

- boot 中的 Image：`6.1.157-android14-11-g78a0a76cd7b7-ab15497637`。
- vendor_boot 中连续排列的 4 份 DTB，字节和顺序保持原样。
- dtbo 中完整 DTBO 表和 entries，移除原厂填充与 AVB footer，由 Lineage 重新签名。
- vendor ramdisk 的 340 个模块，保留 boot/recovery 加载清单与 blocklist。
- vendor_dlkm 的 313 个模块、system_dlkm 的 60 个模块及原始依赖元数据。

用户空间编译需要的 UAPI 头文件仍从 MiCode 源码执行 headers_install 导出；
通过 TARGET_FORCE_PREBUILT_KERNEL 保证 Image 使用原厂文件，不编译源码内核
或源码模块。这些头文件用于编译用户空间，不替换原厂模块的 KMI 数据。

不复用原厂整个 ramdisk、boot.img 或 vendor_boot.img。
Lineage 仍生成 init_boot、vendor_boot、recovery 以及 AVB 信息。
ramdisk/recovery 模块通过 Android 的 BOARD_*_KERNEL_MODULES 接口安装，
不 strip，依赖表由 depmod 生成；两份 DLKM 模块树按原始布局复制。
system_dlkm 的版本子目录必须保留：
原厂 `system_dlkm_modprobe.sh` 会逐个子目录寻找 `modules.load`，
vendor 的 `modules.dep` 也包含这些完整路径。不能简单拍平成一个目录。

此模式不编译、不拼入先前的源码 .ko，也不使用源码模式中裁剪后的模块加载清单。
模块校验信息、签名和二进制内容保持不变。
这只解决内核与驱动配套问题，完整 ROM 仍需编译，并在真机验证挂载、
SELinux、显示、触控、无线、相机和 vendor HAL 等行为。

## 重提取

先按 bringup.md 将完整 Fastboot ROM 展开，包含 vendor、vendor_dlkm、
system_dlkm，再执行：

```sh
python3 device/xiaomi/houji/extract-kernel.py /path/to/rom/images
cd vendor/xiaomi/houji/kernel/stock
sha256sum -c SHA256SUMS
```

脚本限定本次 vendor 基线，检查模块架构与加载清单引用；成功后才替换
`kernel/stock/`，记录输入镜像 SHA-256、模块数量和所有提取文件的哈希。
vendor 基线更新时须同步修改提取脚本中的 ROM_VERSION，并重提取整套文件，
不能只换 Image 或从其他机型拼模块。

## 构建

```sh
source build/envsetup.sh
lunch lineage_houji-bp4a-userdebug
m -j24 bootimage vendorbootimage dtboimage recoveryimage system_dlkmimage vendor_dlkmimage
m -j24 bacon
```

切换模式前先保存或清理旧的产品输出。本次将之前源码模式的
`out/target/product/houji` 整体移至 `out/houji-source-product-20261117`，
保留源码移植成果并确保当前分区目录没有残留的源码模块。
不添加单元测试，使用真实构建、镜像解包与哈希比对验证。
