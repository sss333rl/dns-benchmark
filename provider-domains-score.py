#! /usr/bin/env python3

import json
import sys
import math


# 算法说明：
# 1. 响应成功率 (40分)
# 我们可以使用logistic函数来平滑评分,使得分数在极高成功率时更有区分度
# 2. 错误率 (20分)
# 使用指数衰减函数来惩罚错误
# 3. 延迟性能 (30分)
# 使用多个百分位数据来综合评估延迟:
# 每秒查询数 (QPS) (10分)
# 使用对数函数来评估QPS,这样可以在低QPS时更敏感,高QPS时更平缓
# 总分计算:
# 总分 = 响应成功率分数 + 错误率分数 + 延迟分数 + QPS分数
# 这个评分系统更加科学和客观,因为:
# 使用了非线性函数(如logistic、指数、对数)来更准确地反映各指标的重要性。
# 考虑了多个延迟百分位数,给出更全面的延迟评估。
# 对于极端情况(如非常高的成功率或非常低的错误率)有更好的区分度。
def score_dns_server(data):
    def success_rate_score():
        success_rate = data["totalSuccessResponses"] / data["totalRequests"]
        x = (success_rate - 0.9) * 100
        return 40 / (1 + math.exp(-x))

    def error_rate_score():
        error_rate = (
            data["totalErrorResponses"]
            + data["totalIOErrors"]
            + data["TotalIDmismatch"]
        ) / data["totalRequests"]
        return 20 * math.exp(-10 * error_rate)

    def latency_score():
        def single_latency_score(latency, baseline):
            return math.exp(-latency / baseline) * 10

        p50_score = single_latency_score(data["latencyStats"]["p50Ms"], 100)
        p90_score = single_latency_score(data["latencyStats"]["p90Ms"], 200)
        p99_score = single_latency_score(data["latencyStats"]["p99Ms"], 500)

        return p50_score + p90_score + p99_score

    def qps_score():
        return min(10, 2 * math.log2(data["queriesPerSecond"]))

    success_score = success_rate_score()
    error_score = error_rate_score()
    latency_score = latency_score()
    qps_score = qps_score()

    total_score = success_score + error_score + latency_score + qps_score

    return {
        "total_score": round(total_score, 2),
        "success_rate_score": round(success_score, 2),
        "error_rate_score": round(error_score, 2),
        "latency_score": round(latency_score, 2),
        "qps_score": round(qps_score, 2),
    }


## main
if len(sys.argv) != 2:
    print("使用方法: python3 provider-domains-sort.py results.json")
    sys.exit(1)

# 读取结果文件
with open(sys.argv[1], "r") as result_file:
    results = json.load(result_file)

# 遍历所有 provider
for provider, data in results.items():
    # 提取域名或 IP
    if "://" in provider:
        domain = provider.split("://")[-1].split("/")[0].split(":")[0]
    else:
        domain = provider

    score = score_dns_server(data)

    print(f"{provider}: {score['total_score']}")
    results[provider]["scores"] = score

# 保存结果
with open("results-with-score.json", "w") as f:
    json.dump(results, f, indent=2)

print("处理完成，结果已保存到 results-with-score.json")
