#!/bin/bash

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <输入文件>"
    exit 1
fi

INPUT_FILE="$1"
NAME="${INPUT_FILE%.json}"
OUTPUT_FILE="${NAME}.html"
TEMPLATE_FILE="template.html"

# 检查文件存在性
for file in "$INPUT_FILE" "$TEMPLATE_FILE"; do
    [ -f "$file" ] || {
        echo "错误: 文件 $file 不存在"
        exit 1
    }
done

echo "输入文件: $INPUT_FILE"
echo "输出文件: $OUTPUT_FILE"
echo "模板文件: $TEMPLATE_FILE"

# 读取JSON数据并进行转义
JSON_DATA=$(sed 's/"/\\"/g' <"$INPUT_FILE" | tr -d '\n')

# 使用sed替换模板中的占位符
sed "s|{ JSON_DATA }|$JSON_DATA|g" "$TEMPLATE_FILE" >"$OUTPUT_FILE"

# 检查sed命令是否成功执行
if [ $? -eq 0 ]; then
    echo "HTML文件已生成: $OUTPUT_FILE"

    # 打开输出文件
    open "$OUTPUT_FILE"
else
    echo "错误: 生成HTML文件时出现问题"
    exit 1
fi
