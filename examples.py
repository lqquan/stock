#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票分析器使用示例
"""

from stock_analyzer import StockAnalyzer
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

def example_single_stock_analysis():
    """单支股票分析示例"""
    print("\n===== 示例1: 单支股票分析 =====")
    
    analyzer = StockAnalyzer()
    stock_code = "000001"  # 平安银行
    
    # 获取分析报告
    report = analyzer.analyze_stock(stock_code)
    
    # 打印主要结果
    print(f"股票: {report['stock_code']}")
    print(f"评分: {report['score']}")
    print(f"建议: {report['recommendation']}")
    
    return report

def example_historical_analysis():
    """历史数据分析示例"""
    print("\n===== 示例2: 历史数据分析 =====")
    
    analyzer = StockAnalyzer()
    stock_code = "600519"  # 贵州茅台
    
    # 设置历史时间段
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 一年的数据
    
    # 获取和处理数据
    df = analyzer.get_stock_data(
        stock_code, 
        start_date=start_date.strftime('%Y%m%d'),
        end_date=end_date.strftime('%Y%m%d')
    )
    
    # 计算技术指标
    df = analyzer.calculate_indicators(df)
    
    # 打印数据形状
    print(f"获取数据: {df.shape[0]} 行 x {df.shape[1]} 列")
    print(f"起始日期: {df['date'].min().strftime('%Y-%m-%d')}")
    print(f"结束日期: {df['date'].max().strftime('%Y-%m-%d')}")
    
    # 展示最新的几个技术指标
    print("\n最新技术指标:")
    latest = df.iloc[-1]
    print(f"收盘价: {latest['close']:.2f}")
    print(f"MA5: {latest['MA5']:.2f}")
    print(f"MA20: {latest['MA20']:.2f}")
    print(f"RSI: {latest['RSI']:.2f}")
    print(f"MACD: {latest['MACD']:.4f}")
    
    return df

def example_market_scan():
    """市场扫描示例"""
    print("\n===== 示例3: 市场扫描 =====")
    
    analyzer = StockAnalyzer()
    
    # 定义一系列股票
    stock_list = [
        "000001",  # 平安银行
        "600036",  # 招商银行
        "000651",  # 格力电器
        "600519",  # 贵州茅台
        "000333",  # 美的集团
        "601318",  # 中国平安
        "600276",  # 恒瑞医药
        "000858",  # 五粮液
        "600887",  # 伊利股份
        "601888"   # 中国中免
    ]
    
    # 设置最小评分
    min_score = 60
    
    # 进行市场扫描
    print(f"正在扫描 {len(stock_list)} 只股票...")
    recommendations = analyzer.scan_market(stock_list, min_score)
    
    # 打印结果
    print(f"\n找到 {len(recommendations)} 只推荐股票 (评分 >= {min_score}):")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['stock_code']} - 评分: {rec['score']} - 建议: {rec['recommendation']}")
    
    # 保存结果到CSV
    if recommendations:
        results_df = pd.DataFrame(recommendations)
        csv_file = "market_scan_results.csv"
        results_df.to_csv(csv_file, index=False)
        print(f"\n结果已保存至 {csv_file}")
    
    return recommendations

def example_custom_parameters():
    """自定义参数示例"""
    print("\n===== 示例4: 自定义参数 =====")
    
    # 创建带自定义参数的分析器
    analyzer = StockAnalyzer()
    
    # 修改参数
    analyzer.params = {
        'ma_periods': {'short': 10, 'medium': 30, 'long': 90},  # 改变MA周期
        'rsi_period': 14,
        'bollinger_period': 20,
        'bollinger_std': 2,
        'volume_ma_period': 15,  # 改变成交量MA周期
        'atr_period': 14
    }
    
    # 分析股票
    stock_code = "000858"  # 五粮液
    print(f"使用自定义参数分析股票: {stock_code}")
    
    report = analyzer.analyze_stock(stock_code)
    
    # 展示结果
    print(f"评分: {report['score']}")
    print(f"建议: {report['recommendation']}")
    
    return report

if __name__ == "__main__":
    # 运行所有示例
    example_single_stock_analysis()
    example_historical_analysis()
    example_market_scan()
    example_custom_parameters()
    
    print("\n所有示例已完成运行!") 