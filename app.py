#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from stock_analyzer import StockAnalyzer
import logging
from waitress import serve
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO,
                  format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__, static_folder='static')

# 添加CORS支持
CORS(app)

# 初始化股票分析器
analyzer = StockAnalyzer()

@app.route('/')
def index():
    """首页"""
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': '股票分析服务运行正常'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    """分析单只股票的接口，返回格式化结果供大模型使用"""
    data = request.json
    
    # 验证输入
    if not data or 'stock_code' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供有效的股票代码'
        }), 400
    
    stock_code = data['stock_code']
    
    try:
        # 分析股票
        report = analyzer.analyze_stock(stock_code)
        
        # 提取关键数据并格式化
        formatted_result = {
            # 股票基本信息
            "basic_info": {
                "stock_code": stock_code,
                "analysis_date": report['analysis_date'],
                "price": round(report['price'], 2),
                "price_change": round(report['price_change'], 2)
            },
            # 分析评分和建议
            "analysis_summary": {
                "score": report['score'],
                "recommendation": report['recommendation'],
                "category_scores": report['category_scores'],
                "score_details": report['score_details']
            },
            # 技术指标
            "technical_indicators": {
                "ma_trend": report['ma_trend'],
                "rsi": round(report['rsi'], 2),
                "macd_signal": report['macd_signal'],
                "volume_status": report['volume_status'],
                "adx": round(report.get('adx', 0), 2),
                "stoch_k": round(report.get('stoch_k', 0), 2),
                "stoch_d": round(report.get('stoch_d', 0), 2),
                "cci": round(report.get('cci', 0), 2),
                "mfi": round(report.get('mfi', 0), 2),
                "obv_trend": report.get('obv_trend', '未知'),
                "volatility": round(report.get('volatility', 0), 2),
                "z_score": round(report.get('z_score', 0), 2)
            }
        }
        
        # 添加分析描述文本
        trend_description = "上升" if report['ma_trend'] == "UP" else "下降"
        volume_description = "放量" if report['volume_status'] == "HIGH" else "成交量正常"
        
        # 生成详细的评分说明
        score_explanation = []
        for category, score in report['category_scores'].items():
            category_name = {
                'trend': '📊 趋势类',
                'momentum': '⚡ 动量类',
                'volume': '💹 成交量类',
                'volatility': '🧠 波动率类',
                'statistical': '🧮 统计类'
            }.get(category, category)
            
            score_explanation.append(f"{category_name}: {score}分")
        
        score_details = []
        for indicator, detail in report['score_details'].items():
            score_details.append(f"- {indicator}: {detail}")
        
        formatted_result["analysis_text"] = f"""
股票 {stock_code} 分析报告 (生成于 {report['analysis_date']})

当前价格: {formatted_result['basic_info']['price']} 元 (变动: {formatted_result['basic_info']['price_change']}%)
综合评分: {report['score']} 分
投资建议: {report['recommendation']}

评分明细:
{chr(10).join(score_explanation)}

评分详情:
{chr(10).join(score_details)}

📊 趋势类指标:
- 移动平均线趋势: {trend_description}
- MACD信号: {"买入" if report['macd_signal'] == "BUY" else "卖出"}
- ADX(趋势强度): {round(report.get('adx', 0), 2)}
- 布林带位置: {report.get('bb_position', '中轨')}

⚡ 动量类指标:
- RSI指标: {round(report['rsi'], 2)}
- 随机震荡指标: K({round(report.get('stoch_k', 0), 2)}) D({round(report.get('stoch_d', 0), 2)})
- CCI指标: {round(report.get('cci', 0), 2)}
- ROC变动率: {round(report.get('roc', 0), 2)}%

💹 成交量类指标:
- 成交量状态: {volume_description}
- OBV趋势: {report.get('obv_trend', '未知')}
- MFI指标: {round(report.get('mfi', 0), 2)}

🧠 波动率指标:
- 波动率: {round(report.get('volatility', 0), 2)}%
- 标准差: {round(report.get('std_dev', 0), 2)}

🧮 统计类指标:
- Z-Score: {round(report.get('z_score', 0), 2)}

支撑压力位:
- {report.get('support_resistance', '详见图表分析')}
"""
        
        # 构建最终响应
        response = {
            'status': 'success',
            'data': formatted_result
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"分析股票时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'分析股票时出错: {str(e)}'
        }), 500

@app.route('/api/analyze_for_llm', methods=['POST'])
def analyze_stock_for_llm():
    """分析单只股票并返回纯文本结果，专为大型语言模型提供直接可用的输入"""
    data = request.json
    
    # 验证输入
    if not data or 'stock_code' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供有效的股票代码'
        }), 400
    
    stock_code = data['stock_code']
    
    try:
        # 分析股票
        report = analyzer.analyze_stock(stock_code)
        
        # 格式化指标
        price = round(report['price'], 2)
        price_change = round(report['price_change'], 2)
        rsi = round(report['rsi'], 2)
        trend_description = "上升" if report['ma_trend'] == "UP" else "下降"
        volume_description = "放量" if report['volume_status'] == "HIGH" else "成交量正常"
        macd_signal = "买入" if report['macd_signal'] == "BUY" else "卖出"
        
        # 生成评分明细
        score_categories = []
        for category, score in report['category_scores'].items():
            category_name = {
                'trend': '📊 趋势评分',
                'momentum': '⚡ 动量评分',
                'volume': '💹 成交量评分',
                'volatility': '🧠 波动率评分',
                'statistical': '🧮 统计套利评分'
            }.get(category, category)
            
            max_scores = {
                'trend': 40,
                'momentum': 25,
                'volume': 20,
                'volatility': 10,
                'statistical': 5
            }
            
            score_categories.append(f"{category_name}: {score}/{max_scores.get(category, 0)}分")
        
        # 生成关键指标评分详情
        detail_items = []
        for indicator, detail in report['score_details'].items():
            detail_items.append(f"- {indicator}: {detail}")
        
        # 生成分析文本
        analysis_text = f"""# 股票{stock_code}分析报告

## 基本情况
- 分析日期: {report['analysis_date']}
- 当前价格: {price} 元
- 价格变动: {price_change}%
- 综合评分: {report['score']}分
- 投资建议: {report['recommendation']}

## 评分明细
{chr(10).join(score_categories)}

## 评分详情
{chr(10).join(detail_items)}

## 📊 趋势类指标
- 移动平均线趋势: {trend_description}
- MACD信号: {macd_signal}
- ADX(趋势强度): {round(report.get('adx', 0), 2)}
- 布林带位置: {report.get('bb_position', '中轨')}

## ⚡ 动量类指标
- RSI指标: {rsi}
- 随机震荡指标: K({round(report.get('stoch_k', 0), 2)}) D({round(report.get('stoch_d', 0), 2)})
- CCI指标: {round(report.get('cci', 0), 2)}
- ROC(变动率): {round(report.get('roc', 0), 2)}%

## 💹 成交量类指标
- 成交量状态: {volume_description}
- OBV趋势: {report.get('obv_trend', '未知')}
- MFI指标: {round(report.get('mfi', 0), 2)}

## 🧠 波动率指标
- ATR: {round(report.get('atr', 0), 2)}
- 波动率: {round(report.get('volatility', 0), 2)}%
- 标准差: {round(report.get('std_dev', 0), 2)}

## 🧮 统计套利类指标
- Z-Score: {round(report.get('z_score', 0), 2)}

## 支撑与压力位
- {report.get('support_resistance', '详见图表分析')}

## 交易建议
- 根据当前技术指标分析，该股票{report['recommendation']}。
- 综合评分{report['score']}分（满分100分）反映了各项指标的整体情况。
- 指标中得分较高的部分: {", ".join([cat for cat, score in report['category_scores'].items() if score >= max_scores.get(cat, 0) * 0.6])}
- 指标中存在问题的部分: {", ".join([cat for cat, score in report['category_scores'].items() if score < max_scores.get(cat, 0) * 0.4]) or "无明显问题"}
"""
        
        # 返回纯文本
        return Response(analysis_text, mimetype='text/plain; charset=utf-8')
    except Exception as e:
        logger.error(f"为大模型分析股票时出错: {str(e)}")
        error_message = f"分析股票{stock_code}时出错: {str(e)}"
        return Response(error_message, mimetype='text/plain; charset=utf-8', status=500)

@app.route('/api/scan', methods=['POST'])
def scan_market():
    """扫描市场的接口"""
    data = request.json
    
    # 验证输入
    if not data or 'stock_list' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供有效的股票代码列表'
        }), 400
    
    stock_list = data['stock_list']
    min_score = data.get('min_score', 60)
    
    try:
        # 扫描市场
        recommendations = analyzer.scan_market(stock_list, min_score)
        
        return jsonify({
            'status': 'success',
            'data': recommendations,
            'count': len(recommendations)
        })
    except Exception as e:
        logger.error(f"扫描市场时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'扫描市场时出错: {str(e)}'
        }), 500

@app.route('/api/technical_indicators', methods=['POST'])
def get_technical_indicators():
    """获取股票技术指标的接口"""
    data = request.json
    
    # 验证输入
    if not data or 'stock_code' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供有效的股票代码'
        }), 400
    
    stock_code = data['stock_code']
    start_date = data.get('start_date', None)
    end_date = data.get('end_date', None)
    
    try:
        # 获取股票数据
        df = analyzer.get_stock_data(stock_code, start_date, end_date)
        
        # 计算技术指标
        df = analyzer.calculate_indicators(df)
        
        # 转换为字典
        result = df.tail(20).to_dict('records')
        
        return jsonify({
            'status': 'success',
            'data': result,
            'count': len(result)
        })
    except Exception as e:
        logger.error(f"获取技术指标时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取技术指标时出错: {str(e)}'
        }), 500

@app.route('/api/ai_analysis', methods=['POST'])
def get_ai_analysis():
    """获取股票AI分析的接口"""
    data = request.json
    
    # 验证输入
    if not data or 'stock_code' not in data:
        return jsonify({
            'status': 'error',
            'message': '请提供有效的股票代码'
        }), 400
    
    stock_code = data['stock_code']
    
    try:
        # 获取股票数据
        df = analyzer.get_stock_data(stock_code)
        
        # 计算技术指标
        df = analyzer.calculate_indicators(df)
        
        # 获取AI分析
        analysis = analyzer.get_ai_analysis(df, stock_code)
        
        return jsonify({
            'status': 'success',
            'data': {
                'stock_code': stock_code,
                'analysis': analysis
            }
        })
    except Exception as e:
        logger.error(f"获取AI分析时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取AI分析时出错: {str(e)}'
        }), 500

def main():
    """主函数，启动服务器"""
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"启动股票分析服务 at http://{host}:{port}")
    serve(app, host=host, port=port)

if __name__ == '__main__':
    main() 