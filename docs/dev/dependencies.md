# Repo 依赖与个人仓库

入口为 `device/xiaomi/houji/lineage.dependencies`，递归关联 common、vendor、kernel 与
hardware；kernel 的依赖进一步关联官方 DTS 和已公开的外置源码。
所有依赖显式指定 branch，避免跟随上游默认的 lineage-24.0。

五个个人仓库的 origin 使用 `git@github.com:nian0114/...`；原三个源码仓库保留 upstream。
设备树、common、vendor 分支为 `lineage-23.2`，内核保留 `shennong-u-oss`。

## 发布与首次同步

本次仅创建本地提交，未推送。**先将五个个人仓库的相应分支和 LFS 对象推送，
再让其他工作区 repo sync**，否则远端空仓库无法同步。
当前已有独立 git clone 的目录，不应在本地提交未推送时使用 `repo sync --force-sync` 覆盖。

`houji.xml` 是当前依赖图的完整标准 repo manifest，可直接用于新工作区：

```sh
# 已完成 LineageOS lineage-23.2 的 repo init，并安装 Git LFS：
mkdir -p .repo/local_manifests
# 从本仓库取得 docs/dev/houji.xml，保存到该目录后：
repo sync -c -j8
```

当前工作区也已安装同内容的 `.repo/local_manifests/houji.xml`，未执行覆盖式同步。
XML 使用 HTTPS 拉取、SSH 推送；GitHub SSH 的主机信任和账号密钥仍由用户配置。

## Roomservice

此版本 Lineage roomservice 原来强制给 repository 添加 `LineageOS/`。
`vendor/lineage` 本地分支 `houji-lineage-23.2` 已有独立修复提交，支持完整的 owner/repo
和明确的 remote，旧的不带 owner 的写法仍默认 LineageOS。

新工作区若需要 roomservice 根据新增的 lineage.dependencies 自动发现后续依赖，先应用：

```sh
git -C vendor/lineage am "$PWD/device/xiaomi/houji/docs/dev/patches/0001-roomservice-qualified-repositories.patch"
python3 vendor/lineage/build/tools/roomservice.py lineage_houji true
```

已有完整 `houji.xml` 时，标准 repo sync 本身不依赖这个补丁。
以后新增依赖时需同步维护 dependencies 与完整 manifest；不要让同一路径在多个 manifest 中重复定义。
源码不完整和当前内核移植阻塞见 [bringup.md](bringup.md)。
