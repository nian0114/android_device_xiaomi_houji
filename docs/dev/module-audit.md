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

## 未使用的替代外设：移除 10 个名称

| 模块 | 未匹配到的硬件 |
| --- | --- |
| stm_nfc_i2c | st,st21nfc |
| stm_st54se_gpio | st,st54spi_gpio |
| cs35l43_dlkm | cirrus,cs35l43 |
| aw882xx_dlkm | awinic,aw882xx_smartpa / foursemi,fs16xx |
| fs19xx_dlkm | foursemi,fs16xx |
| sia91xx_dlkm | si,sia81xx / sia91xx 及其芯片变体 |
| tfa986x_dlkm | tfa98xx / awinic,aw884xx_smartpa |
| tlv320aic3x_dlkm | TI tlv320aic3x 家族 / tas5411 |
| tef668x_dlkm | nxp,tef668x |
| radio-i2c-rtc6226-qca | rtc6226 / rtc6226-fmtuner |

这些驱动的 OF alias、legacy I2C ID 以及补查的 compatible 字符串
在全部合并树中均无匹配（包括禁用节点），原厂模块反向依赖为空。
其导入接口未发现自行创建 I2C client / platform device 的入口。

保留有活动节点的 NXP nxp-nci 和原厂 cs35l41_dlkm，并保留
fsa4480-i2c、WCD/WSA、SoundWire 等音频基础模块；后者可能由 machine
驱动或自定义总线使用，不能因缺少普通 OF alias 删除。

## 已屏蔽的测试：移除 1 个名称

ipclite_test.ko 已在设备的 modules.blocklist 明确屏蔽。
原厂 vendor_modprobe.sh 会过滤该文件后再调用 modprobe，此测试模块也无原厂
模块反向依赖。因而不再要求打包它；保留真正的 ipclite.ko，
它有活动 DT 节点，且 synx-driver 依赖它。

## 剩余 105 项的保留依据

以下按优先顺序分类，名称去重且各行互斥。它们是当前保留依据，
并不表示每个驱动都已被证实为开机的硬性依赖。

| 依据 | 数量 | 示例 |
| --- | ---: | --- |
| OF alias 匹配活动节点 | 26 | camera、msm_drm、msm_kgsl、nxp-nci、synaptics_tcm2 |
| 无导出 OF alias，但有专用 compatible 字符串匹配活动节点 | 8 | spss_utils、ubwcp、xiaomi_wifi_gpio、wcd939x_slave |
| 原厂其他模块声明依赖 | 30 | miev、metis、mi_schedule、sync_fence、xiaomi_touch |
| 仅找到显式用户空间加载引用 | 1 | sla（stock slad.rc） |
| 上述证据尚不足，继续核查 | 40 | wl2866d、sia91xx_tuning、部分 Xiaomi hook / SoundWire 模块 |

第二组完整名单为 gpu_dump_skip_cdev、lpass_cdc_va_macro_dlkm、
spss_utils、stub_dlkm、swr_haptics_dlkm、ubwcp、wcd939x_slave_dlkm、
xiaomi_wifi_gpio。debug_ext 中通用 shared-dma-pool 字符串不构成专用驱动
匹配证据，因此没有计入该组。

40 个待继续核查的模块如下；“待核查”不能当作“可以删除”：

```text
binder_prio.ko bootinfo.ko bt_fm_slim.ko
cameralog.ko cpq.ko debug_ext.ko
hardwareinfo.ko io_monitor.ko lb.ko
lpass_cdc_wsa2_macro_dlkm.ko lpass_cdc_wsa_macro_dlkm.ko mi_memory.ko
mi_mempool.ko mi_thermal_interface.ko mi_wmark.ko
migt.ko miicmpfilter.ko millet_binder.ko
millet_hs.ko millet_oem_cgroup.ko millet_sig.ko
minet.ko miwill.ko mpam_policy.ko
perf_helper.ko powersave.ko proc_exit.ko
q6_dlkm.ko rt_mod.ko sia91xx_tuning_dlkm.ko
speed_touch.ko swinfo.ko swr_dmic_dlkm.ko
ufs_ffu.ko wcd9378_slave_dlkm.ko wcd937x_slave_dlkm.ko
wcd938x_dlkm.ko wcd938x_slave_dlkm.ko wl28661d.ko
wl2866d.ko
```

部分 WSA macro / SoundWire 节点当前禁用，但这些模块可能参与 machine 驱动的
动态注册；本轮不据此移除。其余 hook / 字符设备还需追踪源码、导出符号以及
用户空间二进制和 sysfs 使用，再决定保留、适配或随使用方一起移除。

## 暂时保留与验证边界

- synaptics_tcm2 有活动触控节点，且依赖 xiaomi_touch。
- msm_drm、msm_kgsl、相机、视频、DSP、音频框架和同步模块仍需补全源码。
- miev、metis、mist、mi_schedule、mi_power、mpbe 等有原厂模块
  反向依赖；不能把小米扩展整体当作无用的优化模块移除。
- wl2866d、wl28661d 和 sia91xx_tuning 暂未找到活动 DT 匹配，
  但仍需核查动态使用、用户空间接口和具体驱动实现，本轮保留。
- 其他无 alias、无反向依赖的驱动仍可能提供字符设备、sysfs 或内核 hook，
  没有足够证据的项目继续保留。

此审计证明的是当前 ROM 与源码 DT 基线下的加载清单适用性；尚无真机启动、
音频、NFC、相机等运行验证。后续更换 ROM / DT 或启用动态 overlay 时应重新核对。
完整构建与剩余缺口记录在 bringup.md；临时 ELF/DT 解析结果保留在 out/houji-module-audit，
不提交生成数据。
