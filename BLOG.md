我测了全世界...的 DNS 服务器

# 测试全世界的 DNS 服务器能否访问及性能 - 超级多

> 文中提到和用到的东西都在 Github 仓库 [dns-benchmark](https://github.com/xxnuo/dns-benchmark/) 里

如题，测试全世界的 DNS 服务器能否访问及性能，一共有 `989` 个 DNS 服务器地址，列表在 `providers.txt` 文件中（包括同一个服务的 UDP、DoH、DoT 地址）。测了 3 个小时，终于测完了。

中部电信，Wi-Fi6E 环境，macOS 14.5，每个服务器测 10 秒。
话不多说，直接上结果。

## 测试结果
