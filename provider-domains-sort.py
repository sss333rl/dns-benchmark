#! /usr/bin/env python3

import json
import sys
import geoip2.database
import socket

if len(sys.argv) != 2:
    print("使用方法: python3 provider-domains-sort.py results.json")
    sys.exit(1)

# 读取结果文件
with open(sys.argv[1], "r") as result_file:
    results = json.load(result_file)

# 初始化 GeoIP 数据库
reader = geoip2.database.Reader("./geo/GeoLite2-Country.mmdb")

# 遍历所有 provider
for provider, data in results.items():
    # 提取域名或 IP
    if "://" in provider:
        domain = provider.split("://")[-1].split("/")[0].split(":")[0]
    else:
        domain = provider

    # 判断是 IP 还是域名
    if ":" in domain or domain.split(".")[-1].isdigit():
        ip_address = domain
    else:
        try:
            ip_address = socket.gethostbyname(domain)
        except socket.gaierror:
            print(f"无法解析域名: {domain}, 默认国外 None")
            results[provider]["geocode"] = "None"
            continue

    # 查询 GeoIP 数据库
    try:
        resp = reader.country(ip_address)
        code = resp.country.iso_code
    except Exception as e:
        code = "None"

    print(f"{provider}: {code}")
    results[provider]["geocode"] = code

# 保存结果
with open("results-with-geo.json", "w") as f:
    json.dump(results, f, indent=2)

print("处理完成，结果已保存到 results-with-geo.json")
