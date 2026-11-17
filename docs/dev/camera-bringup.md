# 相机 bring-up：ABI 与 Ultra HDR

当前默认已统一为国行 3.0.307，wide_ii/tele_ii 模组与调校配置完整提取，
见 [国行基线](vendor-baseline.md)。以下 Global 对照和补充提取流程为问题
定位过程记录；常规重提取使用完整国行来源。

真机初次检查中，Aperture 切换倍率时相机 provider 曾因 Scudo
`invalid chunk state when deallocating` 中止，栈位于
`ChiContext::DestroyPipelineDescriptor` 的输出流包装对象释放路径。
这说明存在堆内存错误，但单凭该栈不能定位最初的损坏位置。

## 已确认的 ABI 缺口

两份原厂相机插件仍依赖当前 unversioned `libtinyxml2.so`：

- `com.xiaomi.plugin.mialgosnsc.so`
- `com.xiaomi.plugin.mialgoaiur.so`

反汇编显示，它们在成员对象和 `fillMotionInfo` 栈对象中分别按 `0x308`
字节保留/清零 `tinyxml2::XMLDocument`，随后调用同名 C++ 构造函数。
当前平台构造函数会写到 `0x36f`，超过这些旧布局对象边界。
同 ROM 原厂 TinyXML2 和已有的 `libtinyxml2-v34` 使用旧布局。

将两份插件的依赖改为 `libtinyxml2-v34`，与已适配的 anchor 插件、
anchorsync 库和 camera.xiaomi 对齐。修改 ELF 依赖并同步 Soong 依赖，
不修改插件指令、不跳过 free，也不关闭 Scudo。保留原始/修复后 SHA-1
及 extractor fixup，使重新提取仍能复现。

## 验证边界

静态检查确认修复后 `.text` 与原厂相同，所有导入的 TinyXML2 符号在
v34 库中可用，相关 Soong 模块依赖指向 v34。

本项修复确认存在的越界写风险，但并不证明已消除倍率切换的全部问题。
需要操作者重新构建安装后，反复切换超广角/主摄/长焦、前后摄并检查
crash buffer 与 provider PID，再验证拍照和录像。若仍在管线销毁时
崩溃，须继续追踪流对象所有权，不能通过屏蔽内存释放规避。

## VIDEO → PHOTO → VIDEO：派生 Ultra HDR 能力

2026-11-17 真机对照确认，Aperture 默认启用 JPEG Ultra HDR。框架为
该 HAL 派生 JPEG/R 能力后，PHOTO 配置的是 `Camera3-P010CompositeStream`：
4080×3072 P010、HLG10，而非普通 JPEG 输出。

此配置下，`MfsrPostFilter_IPE5` 与 `MfsrPostFilter_IPE66` 的输出端口 9
引用同一个 `ChiStreamWrapper` 和 `ChiStream`。退出拍照模式时，
`camera.qcom.so` 的 `ChiContext::DestroyPipelineDescriptor` 遍历输出槽位，
对重复的 wrapper 执行两次 `operator delete`。malloc_debug 的隔离队列
记录到了同一地址的首次释放栈和再次释放栈；普通 allocator 下则由
Scudo 中止 provider。失败地址位于 `camera.qcom.so + 0x2f8bd0`。

将 Aperture 的 Ultra HDR 偏好临时关闭后，同一路径使用普通 JPEG
（BLOB、STANDARD 动态范围）。MFSR 仍会创建，但不再出现上述 IPE66
重复输出。恢复 Ultra HDR 又能复现相同的释放错误。

### 设备配置

在 houji 自己的 system 属性文件中设置 `ro.camera.disableJpegR=true`。
平台已有的 `CameraProviderManager::DeviceInfo3::deriveJpegRTags()` 会读取
该属性并跳过 JPEG/R 能力派生，使相机应用回退到 HAL 可正常处理的
普通 JPEG。该属性是现有的 `camera_config_prop` 布尔属性。

这是针对不兼容流配置的能力限制，不是对闭源 HAL 内部所有权逻辑的
修复。代价是关闭框架派生的 Ultra HDR 照片支持。它不修改 HAL 指令、
内存分配器、Aperture 或平台源码。重新开启该能力前，必须先修正并
验证厂商 P010/HLG 拍照路径的输出所有权。

### 原厂配置与二进制基线

进一步从两份官方包的 `/odm/etc/build.prop` 核对到相同限制：

| 官方版本 | 原件行号 | 属性 |
| --- | --- | --- |
| Global OS3.0.305.0.WNCMIXM | 330 | `ro.camera.disableJpegR=true` |
| CN OS3.0.307.0.WNCCNXM | 337 | `ro.camera.disableJpegR=true` |

Global 的属性文件还通过 `dump.erofs` 获得原始 `odm.img` 的 extent，
直接读取并解压后，与解包文件逐字节核对一致。CN 的属性文件从用户
提供的完整 ODM 镜像中选择性提取，确认版本号及属性。

因此该设备属性是补回原厂已有的兼容性基线，而不是从原厂已开放的
框架能力中额外裁掉 JPEG/R。它解释了移植后 Aperture 为什么进入
原厂配置本来就禁止派生的 P010/HLG 拍照路径。它不能据此说明原厂
相机应用如何实现其自身的 HDR 成片，后者需单独验证。

对当前 Global 基线的五份关键库逐一核对，工程与官方原件的 `.text`
指令区均一致：

- `camera.qcom.so`
- `com.qti.chi.override.so`
- `com.qti.chiusecaseselector.so`
- `com.qti.feature2.mfsr.so`
- `com.qti.feature2.gs.sm8650.so`

其 ELF 依赖表差异对应已有的 allocator V1→V2 适配及 processgroup
shim。`camxoverridesettings.txt` 与 Global 原件逐字节一致。这六个
工程文件的 SHA-256 也与当前真机一致，排除了本次核对使用错误安装
版本的情况。以上范围不代表整个相机依赖闭包均已完成 ABI 验证。

### 验证范围

真机对照通过 Aperture 的 Ultra HDR 开关选择对应流配置，并检查
每个模式的预览时间戳、provider PID 和 native 崩溃日志。普通 JPEG
先连续通过 3 轮；重新开启 Ultra HDR 后第一轮即在同一位置崩溃；
再次关闭后又连续通过 3 轮，共通过 6 轮普通 JPEG 切换。没有启动
Android 构建或添加单元测试。当前手机的 Aperture 已关闭 Ultra HDR，
作为安装新构建前的临时设置；没有刷写
分区或重启整机。工程属性会在下次构建安装后生效，仍需确认应用不再
获得框架派生的 JPEG/R 能力。

本项验证只覆盖默认后摄 VIDEO/PHOTO 预览切换，不代表已经验证拍照
成片、实际录像、全部倍率、前后摄切换或主摄 EEPROM 探测问题。

## 主摄 EEPROM 探测条件（2026-11-17）

进一步只打开 SENSOR 组的 info/verbose 日志，重启 provider 后捕获到：

```text
camxeepromdata.cpp:5240 Compare() 182 eq 181 => false
camxeepromdata.cpp:5349 Probe() Probe item failed
camxeepromdata.cpp:5404 Probe() Probe EEPROM houji_sunny_ovx9000_p24c128e_wide_eeprom failed.
```

这次探测实际读到 `0xB6`，当前 wide 配置要求 `0xB5`，因此主摄被拒绝。
当前属性仍为 `back_main=none`；前摄、超广角、长焦的存在不能算主摄恢复。
当前模组二进制确实包含 `0xB5` 条件。Global 3.0.305 官方目录有 wide 和
wide_ii 的 sensor/EEPROM/actuator 库，但只找到一份 wide sensormodule bin；
CN 3.0.307 已核对的同名 bin 与 Global 相同。这些事实还不能证明 wide_ii
就是该手机应该选择的变体，也不能证明改成接受 B6 就能安全使用相同校准。

下一步需要从这台手机运行原厂系统时，核对实际加载的 sensormodule、
sensor、EEPROM 库、探测日志及运行时补充配置，确定正确的模组匹配路径。
不要通过跳过 probe、把 B5 直接改成 B6、复制 golden 数据或写 EEPROM/persist
校准来伪造探测成功。本次只采集初始化日志，临时日志属性已恢复；未修改
EEPROM/persist 校准、厂商库指令或主摄配置。主摄问题仍未修复。


## Global 原厂真机对照（2026-11-17）

操作者刷回原厂后，通过 ADB 重新采集属性、CameraService 静态信息、
预览会话和全部可读日志。当前为 Global OS3.0.305.0.WNCMIXM user 构建，
活动槽位为 a；bootimage、vendor、odm 的版本属性均指向该 Global 版本。
`ro.boot.hwc=CN`，SELinux 为 Enforcing，诊断使用普通 shell 权限。
这些版本属性用于确认本次基线，不等同于所有分区内容的逐字节校验。

原厂同样报告：

```text
persist.vendor.camera.mi.module.info=back_main=none;back_tele=0x62;
persist.vendor.camera.mi.module.infoext=front_main=0x60;back_ultra=0x62;
persist.vendor.camera.sensor.probe=<front:----S><tele:----S><ultra:----S>
```

不能仅依赖持久属性判断，因为它们可能跨刷机保留。本次同时核对了
当前 Camera HAL 的静态元数据：

| camera ID | 焦距（mm） | 活动阵列 | 识别用途 |
| --- | --- | --- | --- |
| 0 | 2.16 | 4080×3072 | 后置超广角 |
| 1 | 2.83 | 3264×2448 | 前摄 |
| 2 | 9.00 | 4080×3072 | 后置长焦 |
| 3 | 2.16 | 4080×3072 | 后置逻辑相机，physicalIds 为 0、2 |
| 4 | 2.83 | 3264×2448 | 前摄别名 |

CameraService 总数为 7，但其余 ID 5、6 的存在不代表 OVX9000 主摄已
注册。主摄对应的物理设备未出现在上述正常相机及后置逻辑成员中。

将原厂 `com.android.camera/.Camera` 带到前台后，实际预览客户端连接
的是 camera 0。此前应用日志也出现 `SAT lost !`，以及
`updateUltraWideCapability: currZoomRatio = 0.6`。所以“原厂能显示后摄
画面”不能作为主摄正常的证明。本次 crash buffer 为空，未捕获到
provider native 崩溃；这不代表已经验证全部倍率、拍照或录像功能。

结论：主摄未识别在此次 Global 原厂基线上同样存在，不能继续把它
归因于 Lineage 独有的 HAL/内核适配问题。但本机原先使用的是国行
OS3.0.307，尚未取得该版本的正常运行时对照，因此也不能据此判定
硬件损坏。下一步应以原先国行完整固件验证主摄，再决定是否继续追查
地区/版本配置或硬件、校准路径。

本次原厂日志没有捕获到初始化阶段的 EEPROM 比较过程，不能宣称已在
原厂重新测得 B6/B5 不匹配。原厂 shell 无权读取 camera 库、provider
maps 和私有校准目录，未绕过这些限制；未修改属性、库、EEPROM/persist，
未刷写分区、重启服务或整机，也未拍摄。没有启动 ROM 编译。


### 原厂倍率界面与活动镜头

操作者反馈界面提供 0.6×、1×、2×、3.2×，滑动最高到 10×。为避免
仅凭按钮判断硬件，进一步采集界面和当前会话的 request/result 元数据：

| 原厂界面档位 | 活动 camera ID | lens.focalLength（mm） | control.zoomRatio |
| --- | --- | --- | --- |
| 1× | 0 | 2.16 | 1.66666663 |
| 3.2×（操作者手动切换） | 0 | 2.16 | 5.33333302 |

两次预览均落在超广角上，zoomRatio 分别约为界面倍率除以 0.6，
说明当前观察到的是超广角数字变焦，不能把 1× 按钮当作 OVX9000
已经工作的证据。该结论仅覆盖这两次预览；不能据此断言所有光照、
模式和倍率下均不会使用长焦。没有验证照片成片或录制视频。

原厂限制 ADB input 注入，首次点击请求被拒绝，未成功切换档位；
3.2×由操作者手动选择。没有修改开发者安全设置来绕过该限制。


## 国行原厂恢复主摄与 wide_ii 配置补齐（2026-11-17）

随后刷回国行 OS3.0.307.0.WNCCNXM 完整固件，bootimage、vendor、odm
版本属性均指向该版本。普通 ADB shell、SELinux Enforcing 下观察到：

```text
persist.vendor.camera.mi.module.info=back_main=0x74;back_tele=0x62;
persist.vendor.camera.sensor.probe=<front:----S><tele:----S><ultra:----S><wide:----S>
```

当前 HAL 注册 11 个设备，物理 ID 2 为焦距 6.55 mm、活动阵列
4096×3072 的主摄；ID 3 为 2.16 mm 超广角，ID 4 为 9 mm 长焦。
原厂应用连接逻辑 ID 5。操作者切到拍照 1× 后，当前会话元数据
`android.lens.focalLength=6.55000019`、`android.control.zoomRatio=1.0`。
相比 Global 的 1× 超广角数字变焦，本次主摄注册及预览已恢复。
采集时 crash buffer 为空；未验证拍照成片、录像或全部倍率。

### 缺失文件与官方来源

国行 ODM 相比 Global 额外包含两份主摄变体文件，当前工程也缺少它们：

| 文件（位于 odm/lib64/camera） | 国行原件 SHA-1 |
| --- | --- |
| com.qti.sensormodule.houji_sunny_ovx9000_wide_ii.bin | 3d51fcb218b940af98b9d38bdce6f60d60e88ab3 |
| com.qti.tuned.houji_sunny_ovx9000_wide_ii.bin | 7c8c358a334054cd2d7826ac9c5facc1a114217a |

从操作者提供的国行 3.0.307 完整包中提取上述原件。wide_ii 模组包含
`0xB6` 探测条件，并引用对应的 wide_ii sensor、EEPROM、actuator 名称。
这些配套 `.so` 的国行原始 SHA-1 与工程已记录的 Global 原始 hash
逐一相同，现有 allocator fixup 继续适用。原 wide 配置的 B5 条件保持
不变；补入官方变体，不改探测逻辑、不修改 EEPROM/persist 或校准数据。

这解释了为什么原有 wide 探测读到 B6 后失败，以及仅有 wide_ii 驱动库
仍不足以支持该模组。国行原厂对照支持模组配置缺失这一修复方向，
不能再将此次主摄缺失作为硬件故障的证据。原厂没有开放初始化详细
probe 日志及 maps 读取，因此本次未取得其具体库加载轨迹。

### 重复提取与后续验证

在 proprietary-files.txt 的 `Camera CN main sensor variant` 独立 section
中固定两份国行原件 hash，并通过生成的 vendor makefile 安装到 ODM。
默认非 kang 提取会优先保留 vendor 仓库中 hash 匹配的 pinned 文件，
所以从 Global 基线重新提取时可保留这两份补充配置。

若从空 vendor 目录恢复，应先将两份国行原件补入完整 Global 解包目录的
`odm/lib64/camera/`，再运行一次常规提取；仅凭 Global 包无法生成它们。
若 vendor 已有其余文件，只需单独提取国行本节（从 device 目录执行）：

```sh
./extract-files.py --only-target --section 'Camera CN main sensor variant' /path/to/cn307-dump
```

本次只执行文件提取、makefile 生成和静态核对，没有构建 ROM。安装新
Lineage 构建后，仍需验证 wide 探测、主摄物理元数据、1×预览、拍照、
录像及倍率切换；不能把国行原厂的成功直接计作 Lineage 修复已通过。
