#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import List
from stock_analyzer import StockAnalyzer
import logging
import pandas as pd

def main():
    # 设置日志
    logging.basicConfig(level=logging.INFO,
                      format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # 初始化股票分析器
    analyzer = StockAnalyzer()
    
    # 定义要分析的股票代码列表
    # 示例: 格式需符合 akshare 要求 (沪深股票代码)
    stock_list = [
        "000001",  # 平安银行
        "600036",  # 招商银行
        "000651",  # 格力电器
        "600519",  # 贵州茅台
        "000333"   # 美的集团
    ]
    
    try:
        # 单一股票分析示例
        print("\n======= 单一股票分析 =======")
        stock_code = "000001"  # 平安银行
        logger.info(f"开始分析股票: {stock_code}")
        
        report = analyzer.analyze_stock(stock_code)
        
        print(f"股票代码: {report['stock_code']}")
        print(f"分析日期: {report['analysis_date']}")
        print(f"评分: {report['score']}")
        print(f"价格: {report['price']:.2f}")
        print(f"价格变动: {report['price_change']:.2f}%")
        print(f"MA趋势: {report['ma_trend']}")
        print(f"RSI: {report['rsi']:.2f}")
        print(f"MACD信号: {report['macd_signal']}")
        print(f"成交量状态: {report['volume_status']}")
        print(f"建议: {report['recommendation']}")
        print("\nAI分析:")
        print(report['ai_analysis'])
        
        # 市场扫描示例
        print("\n======= 市场扫描 =======")
        logger.info("开始市场扫描")
        min_score = 60
        recommendations = analyzer.scan_market(stock_list, min_score)
        
        print(f"找到 {len(recommendations)} 只推荐股票 (评分 >= {min_score}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['stock_code']} - 评分: {rec['score']} - 建议: {rec['recommendation']}")
            
        # 将结果保存为CSV
        if recommendations:
            logger.info("保存推荐结果到CSV文件")
            results_df = pd.DataFrame(recommendations)
            results_df.to_csv("stock_recommendations.csv", index=False)
            print("结果已保存至 stock_recommendations.csv")
            
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}")


if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
