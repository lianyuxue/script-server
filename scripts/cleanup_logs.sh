#!/bin/bash

DAYS=$1
PATH=$2
DRY_RUN=$3

echo "===== 日志清理工具 ====="
echo "参数说明："
echo "  - 保留天数: $DAYS 天"
echo "  - 清理目录: $PATH"
echo "  - 模拟运行: $DRY_RUN"
echo ""

if [ "$DRY_RUN" = "true" ] || [ "$DRY_RUN" = "--dry-run" ]; then
    echo "⚠️  这是模拟运行，不会实际删除文件"
    echo ""
    echo "将删除的文件:"
    find "$PATH" -name "*.log" -type f -mtime +$DAYS
else
    echo "🔧 正在执行清理..."
    COUNT=$(find "$PATH" -name "*.log" -type f -mtime +$DAYS -print -delete | wc -l)
    echo ""
    echo "✅ 清理完成！共删除 $COUNT 个日志文件"
fi

echo ""
echo "===== 任务完成 ====="
