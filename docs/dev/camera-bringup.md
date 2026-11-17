# 相机 bring-up：TinyXML2 对象布局

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
