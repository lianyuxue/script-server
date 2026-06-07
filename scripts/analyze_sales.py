#!/usr/bin/env python3
import sys
import os
import csv
from datetime import datetime, timedelta

def parse_args():
    args = sys.argv[1:]
    mode = args[0] if len(args) > 0 else "summary"
    date_range = args[1] if len(args) > 1 else "month"
    return mode, date_range

def generate_report(mode, date_range):
    print("===== 销售数据分析 =====")
    print(f"分析模式: {mode}")
    print(f"时间范围: {date_range}")
    print("")
    
    # 模拟生成一些数据
    now = datetime.now()
    data = []
    
    # 根据日期范围生成数据
    if date_range == "today":
        days = 1
    elif date_range == "week":
        days = 7
    elif date_range == "month":
        days = 30
    elif date_range == "year":
        days = 365
    else:
        days = 90
    
    total_sales = 0
    for i in range(days):
        date = now - timedelta(days=i)
        sales = 1000 + (i * 5) + (date.day * 10)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "sales": sales,
            "orders": 10 + (i % 5) * 2
        })
        total_sales += sales
    
    # 根据模式输出
    if mode == "summary":
        print("📊 销售摘要：")
        print(f"总销售额: ${total_sales:,.2f}")
        print(f"日均销售额: ${total_sales/days:,.2f}")
        print(f"统计天数: {days} 天")
    elif mode == "detailed":
        print("📊 销售摘要：")
        print(f"总销售额: ${total_sales:,.2f}")
        print(f"日均销售额: ${total_sales/days:,.2f}")
        print("")
        print("最近 7 天销售明细：")
        for i, row in enumerate(data[:7]):
            print(f"  {row['date']}: ${row['sales']:,.2f} ({row['orders']} 订单)")
    else:
        print("📊 完整分析报告：")
        print(f"总销售额: ${total_sales:,.2f}")
        print(f"日均销售额: ${total_sales/days:,.2f}")
        print(f"最大单日销售: ${max([r['sales'] for r in data]):,.2f}")
        print(f"最小单日销售: ${min([r['sales'] for r in data]):,.2f}")
        print("")
        print("完整销售数据（前 10 天）：")
        for i, row in enumerate(data[:10]):
            print(f"  {row['date']}: ${row['sales']:,.2f} ({row['orders']} 订单)")
    
    # 生成输出文件
    generate_csv_report(data)
    
    print("")
    print("===== 分析完成 =====")
    print("✅ 报告已生成: analysis_report.csv")

def generate_csv_report(data):
    with open("analysis_report.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["date", "sales", "orders"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    mode, date_range = parse_args()
    generate_report(mode, date_range)
