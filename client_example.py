#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
股票分析器API客户端示例
"""

import requests
import json
import pandas as pd
from datetime import datetime

class StockAnalyzerClient:
    """股票分析器API客户端"""
    
    def __init__(self, base_url="http://localhost:5000/api"):
        """初始化客户端"""
        self.base_url = base_url
    
    def health_check(self):
        """健康检查"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def analyze_stock(self, stock_code):
        """分析单只股票（返回JSON格式）"""
        response = requests.post(
            f"{self.base_url}/analyze",
            json={"stock_code": stock_code}
        )
        return response.json()
    
    def analyze_stock_for_llm(self, stock_code):
        """分析单只股票（返回格式化文本，适用于大模型）"""
        response = requests.post(
            f"{self.base_url}/analyze_for_llm",
            json={"stock_code": stock_code}
        )
        return response.text
    
    def scan_market(self, stock_list, min_score=60):
        """扫描市场"""
        response = requests.post(
            f"{self.base_url}/scan",
            json={"stock_list": stock_list, "min_score": min_score}
        )
        return response.json()
    
    def get_technical_indicators(self, stock_code, start_date=None, end_date=None):
        """获取技术指标"""
        data = {"stock_code": stock_code}
        if start_date:
            data["start_date"] = start_date
        if end_date:
            data["end_date"] = end_date
            
        response = requests.post(
            f"{self.base_url}/technical_indicators",
            json=data
        )
        return response.json()
    
    def get_ai_analysis(self, stock_code):
        """获取AI分析"""
        response = requests.post(
            f"{self.base_url}/ai_analysis",
            json={"stock_code": stock_code}
        )
        return response.json()

def print_separator():
    """打印分隔符"""
    print("\n" + "="*80 + "\n")

def save_to_file(content, filename):
    """保存内容到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"结果已保存至文件: {filename}")

def main():
    """主函数"""
    # 初始化客户端
    client = StockAnalyzerClient()
    
    try:
        # 1. 健康检查
        print("1. 健康检查")
        result = client.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print_separator()
        
        # 2. 分析单只股票（JSON格式）
        stock_code = "000001"  # 平安银行
        print(f"2. 分析股票: {stock_code} (JSON格式)")
        result = client.analyze_stock(stock_code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print_separator()
        
        # 3. 分析单只股票（大模型格式）
        print(f"3. 分析股票: {stock_code} (大模型格式)")
        llm_text = client.analyze_stock_for_llm(stock_code)
        print(llm_text)
        
        # 保存到文件，方便传递给大模型
        analysis_filename = f"analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        save_to_file(llm_text, analysis_filename)
        print_separator()
        
        # 4. 扫描市场
        stock_list = ["000001", "600036", "000651", "600519", "000333"]
        min_score = 60
        print(f"4. 扫描市场 (评分 >= {min_score})")
        result = client.scan_market(stock_list, min_score)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print_separator()
        
        # 5. 获取技术指标
        print(f"5. 获取技术指标: {stock_code}")
        result = client.get_technical_indicators(stock_code)
        # 将结果转换为DataFrame以便更好地显示
        if result["status"] == "success":
            df = pd.DataFrame(result["data"])
            print(df.tail().to_string())
        else:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        print_separator()
        
        # 6. 获取AI分析
        print(f"6. 获取AI分析: {stock_code}")
        result = client.get_ai_analysis(stock_code)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 