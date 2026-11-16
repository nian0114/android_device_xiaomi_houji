# houji 模块加载清单适用性核对

## 范围与方法

基线为国际版 Fastboot 包 OS3.0.305.0.WNCMIXM，与当前 vendor 提取基线一致。
使用该包 vendor_boot 中全部 4 个基础 DTB，分别应用该包 dtbo.img 中的 houji
overlay；另核对源码构建的 Pineapple / Pineapple-v2 两个 houji 合并 DTB。
检查节点状态时包含全部祖先节点，不能把禁用总线下的节点当成活动硬件。

对原厂 495 个模块读取 modinfo 的 OF/I2C alias 和 depends，检查反向依赖；
对没有 OF alias 的驱动补查 ELF 中的 compatible 字符串，并检查驱动导入的
总线注册和动态设备创建接口。I2C 检查还覆盖 compatible 去厂商前缀后的
legacy ID 匹配，不能仅凭缺少 MODULE_DEVICE_TABLE 删除驱动。
另检查 device/common 和 stock 分区 init、配置脚本中的显式加载引用。

本轮只缩小设备要求的模块清单，不修改主树、内核实现或缺失检查，
不复用 stock .ko，不把缺失模块全部视为必需或全部视为可选。
各清单会移除对应模块的所有重复项，其余条目的顺序保持不变。

## 其他高通平台：移除 10 个名称

| 模块 | 原厂驱动匹配目标 |
| --- | --- |
| camcc-volcano | qcom,volcano-camcc |
| dispcc-volcano | qcom,volcano-dispcc |
| gcc-volcano | qcom,volcano-gcc |
| gpucc-volcano | qcom,volcano-gpucc |
| pinctrl-volcano | qcom,volcano-pinctrl / volcano-vm-pinctrl |
| qnoc-volcano | Volcano 的各 NoC 节点 |
| videocc-volcano | qcom,volcano-videocc |
| phy-qcom-ufs-qmp-v4-crow | qcom,ufs-phy-qmp-v4-crow |
| debugcc-volcano | qcom,volcano-debugcc（ELF 字符串） |
| debugcc-cliffs | qcom,cliffs-debugcc（ELF 字符串） |

以上匹配在 6 份合并树中均不存在，原厂模块反向依赖均为空。
debugcc 两项虽未导出 OF alias，但其 ELF 中的平台匹配字符串可识别；
导入接口显示注册 platform driver，没有自建 platform device 的导入。
houji 的 Pineapple/Pineapplep 时钟、互联与 UFS 驱动仍保留。

