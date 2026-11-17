# 国行 vendor 基线

当前默认基线为用户提供的 Xiaomi 14 国行完整 Fastboot 包
`OS3.0.307.0.WNCCNXM`，硬件型号 `23127PN0CC`。houji 与
sm8650-common 的用户空间文件、固件及默认原厂内核均从同一包提取。

原始 `super.img` SHA-256：
`6866956b2cae1bc286edeb56b5271d33580f561ffaef8adfdad932b520ea3ce2`。

## 提取范围

| 内容 | 数量 / 版本 |
| --- | --- |
| 用户空间文件 | 3,192（houji 1,588，common 1,604） |
| Fastboot 固件 | 21，包含同版 modem / modemfirmware |
| 默认原厂内核 | 6.1.138-android14-11-g0c3d559bcd85-ab14529422 |
| vendor ramdisk 模块 | 340 |
| vendor_dlkm 模块 | 314 |
| system_dlkm 模块 | 60，保留版本目录 |
| DTB | 4，保留原始顺序 |
| Vendor 安全补丁声明 | 2026-08-01 |

国行包的内核与此前 Global 6.1.157 不同，因此连同 Image、DTB、DTBO、
ramdisk/DLKM 模块及加载元数据整套更新。国行多出的 `tango32.ko` 一并
按原厂打包。源代码内核及早期 Global 模块审计材料属于可选开发路径；
默认模式使用 `vendor/xiaomi/houji/kernel/stock/` 的上述国行配套。

国行相机的 wide_ii 和 tele_ii 模组配置及调校文件均已纳入清单。
既有 wide/tele 变体继续按原厂配置探测；本轮不修改 EEPROM 校验或校准。

按产品要求移除 Google Hotword enrollment 的两份 APK、专用 Java util
及权限声明，以及 SoterService APK。专用 enrollment 权限白名单也已删除。
原厂原生音频及安全 HAL 仍按设备清单提取。

## 保留的兼容修复

直接对国行原件执行现有 extract-files.py fixup，再固定原始及修复后 hash。
保留相机 TinyXML2 v34、GraphicBuffer/allocator、processgroup 等适配，
以及显示、音频与 Binder shim 依赖。Codec2 服务继续使用原厂实现。

国行原始 perfboostsconfig.xml、media_codecs.xml 和
media_codecs_pineapple.xml 与之前核对的 Global 原件逐字节相同，
性能 fallback 与 Dolby include 修复继续适用。设备 SELinux、camlog、
ramdump、振动库和禁用框架派生 JPEG/R 等独立修复继续保留。

## 复现与验证

按 [开发基线](bringup.md) 展开完整国行包，先确认 vendor/odm 的
`ro.*.build.version.incremental=OS3.0.307.0.WNCCNXM`，再提取两个模块
及原厂内核。新包迁移时使用 --kang 更新原始/修复后 pin；常规重提取
使用默认 pin 校验。固件依赖 Git LFS，提交与推送需要完整 LFS 对象。

本次先在独立目录提取：完整展开 vendor、odm、vendor_dlkm、system_dlkm，
按清单从 system、system_ext、product 选择提取所需文件。服务器的
`out/vendor-rom/OS3.0.307.0.WNCCNXM/images` 可用于当前清单重提取；
增加这些选择性展开分区的条目时，应从完整 Fastboot 镜像重新展开。

已核对四份完整分区在本机/服务器的 SHA-256、25 份启动/固件输入摘要、
清单内每项原始和修复后 SHA-1、APK/JAR 完整性、配套模块架构与加载引用、
kernel/stock/SHA256SUMS，以及关键相机 ABI、perf/Dolby 配置和应用移除规则。
来源和内核数量也记录在 kernel/stock/provenance.json。

本次没有运行 ROM 编译或刷写手机。安装前保存并清理旧产品输出，重新
构建同一次的启动镜像和整包，避免旧 6.1.157 模块目录混入。完整编译、
Lineage 下的主摄/倍率/拍照录像、无线、音频和服务稳定性仍需验证；
国行原厂的正常主摄预览不能计作新 Lineage 构建已经验证。
