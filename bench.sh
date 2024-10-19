#!/bin/bash

# 本脚本用到的命令行工具：dnspyre、jq

# 从 providers.txt 文件中读取 DNS 服务器地址列表，每行一个地址
SERVERS=()
while IFS= read -r line || [[ -n "$line" ]]; do
    # 忽略空行和以#开头的注释行
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        SERVERS+=("$line")
    fi
done < providers.txt

# 检查是否成功读取了服务器地址
if [ ${#SERVERS[@]} -eq 0 ]; then
    echo "错误：未能从 providers.txt 文件中读取到任何有效的 DNS 服务器地址"
    exit 1
fi

echo "成功读取 ${#SERVERS[@]} 个 DNS 服务器地址"

# 域名列表路径，以@开头表示相对路径，或者是网址
DOMAINS="@dnspyre/data/1000-domains"

# 持续时间
DURATION="10s"
# 并发数
CONCURRENCY=10

# 开始，检测必须工具是否存在
if ! command -v dnspyre &>/dev/null; then
    echo "dnspyre 未安装"
    exit 1
fi
if ! command -v jq &>/dev/null; then
    echo "jq 未安装"
    exit 1
fi

# 生成一个0到1之间的两位小数作为随机域名列表种子
SEED=$(awk 'BEGIN{srand(); printf "%.2f", rand()}')
echo "随机种子: $SEED"

# 开始时间，示例：2024-10-19T15:43:30+08:00
START_TIME=$(date +"%Y-%m-%dT%H:%M:%S+08:00")

# 初始化 results.json 为空的 JSON 对象
echo '{}' >results-$START_TIME.json

for SERVER in "${SERVERS[@]}"; do
    # 根据上面的命令生成命令
    CMD="dnspyre --duration $DURATION -c $CONCURRENCY -t A -t AAAA --json --no-distribution $DOMAINS --probability $SEED --server $SERVER"
    # 执行命令，并将命令返回的 json 以 SERVER 为 key 添加到 results.json 文件中
    echo "正在测试服务器: $SERVER"
    RESULT=$(eval $CMD)
    if [ $? -eq 0 ]; then
        # 将结果添加到 JSON 文件中
        jq --arg server "$SERVER" --argjson result "$RESULT" '. + {($server): $result}' results-$START_TIME.json >temp.json && mv temp.json results-$START_TIME.json
        echo "服务器 $SERVER 的测试结果已添加到 results-$START_TIME.json"
    else
        echo "服务器 $SERVER 测试失败"
    fi
done
