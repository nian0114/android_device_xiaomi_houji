# 国行设备的基带固件

当前测试手机是国行小米 14（`ro.boot.hwc=CN`），原系统为
`OS3.0.307.0.WNCCNXM`。初次安装本项目 ROM 后，国际版基带可以启动并
返回版本，但两路 `RADIO_POWER on=true` 都返回错误 71：
`NO_RF_CALIBRATION_INFO`，框架保持 `POWER_OFF`。这不等同于校准分区损坏。

## 固定国行基带配对

为恢复原来的无线电固件基线，本设备树将以下两项一同固定到用户提供的
国行 3.0.307 Fastboot 包。当前其他固件、原厂内核、userspace vendor/IMS
也已统一为同版国行基线，见 [国行基线](vendor-baseline.md)。两版固件的文件清单确实不同，不能仅凭基带启动成功
判定射频兼容。更换后仍须真机验证，不能预先声称已恢复信号。

| 源文件 | vendor 仓库路径 | SHA-256 |
| --- | --- | --- |
| NON-HLOS.bin | radio/modem.img | 3ccb918129b84228c6e3454969a83ba24f6df5e72ca10488e9044a0d11c21d8b |
| MODEM-FW.bin | radio/modemfirmware.img | 66dcc89d63d047a8d0a1f70139c09f7378d82387e21d83fa062636447b5315fa |

`proprietary-firmware.txt` 的两个 SHA-1 pin 与 vendor `Android.mk` 保持一致，
以便后续 OTA 继续打包这对固件。先完整拉取 vendor Git LFS 对象，再执行
正常提取，extract-utils 会保留匹配 pin 的文件。不要对国际版包执行不加
区分的 `--kang` 并覆盖这两个 pin；重新生成文件时检查这两项来源与摘要。
本选择针对国行测试机，国际版实体机需要重新核定地区基带。

## 安装和验证

本轮检查的活动槽位为 b。操作者再次用 `fastboot getvar current-slot` 确认后，
可将上述两个原始文件分别刷至当前槽的 `modem_b`、`modemfirmware_b`，然后
重启进入系统。此操作会改变基带固件，执行前应保存之前使用的固件包。
不需要修改 persist、modemst1、modemst2、fsg 或 fsc，也不需要关闭 AVB。

安装后读取 radio buffer：应不再出现 `RADIO_POWER` 的错误 71，服务状态应
离开 `POWER_OFF` 并正常注册运营商。随后由操作者验证电话、短信、数据和
IMS。若仍报错，应继续检查原厂 NV/校准访问和固件组合，不能擦除校准分区。
