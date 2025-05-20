# 股票分析器 API 文档

本文档描述了股票分析器服务的API接口。

## 基本信息

- 基础URL: `http://服务器IP:5000/api`
- 所有POST请求的Content-Type应为 `application/json`
- 所有响应都以JSON格式返回，除了特别说明的接口

## 接口列表

### 1. 健康检查

检查API服务是否正常运行。

- **URL:** `/health`
- **方法:** `GET`
- **响应示例:**

```json
{
  "status": "ok",
  "message": "股票分析服务运行正常"
}
```

### 2. 分析单只股票

对单只股票进行全面分析，返回结构化的JSON数据。

- **URL:** `/analyze`
- **方法:** `POST`
- **请求参数:**

```json
{
  "stock_code": "000001"  // 股票代码，必填
}
```

- **响应示例:**

```json
{
  "status": "success",
  "data": {
    "basic_info": {
      "stock_code": "000001",
      "analysis_date": "2023-08-15",
      "price": 10.55,
      "price_change": 1.23
    },
    "analysis_summary": {
      "score": 75,
      "recommendation": "建议买入"
    },
    "technical_indicators": {
      "ma_trend": "UP",
      "rsi": 58.42,
      "macd_signal": "BUY",
      "volume_status": "HIGH"
    },
    "ai_analysis": "详细的AI分析内容...",
    "analysis_text": "格式化的分析文本摘要..."
  }
}
```

### 3. 分析单只股票（大模型格式）

对单只股票进行全面分析，返回格式化的纯文本结果，专为传递给大型语言模型设计。

- **URL:** `/analyze_for_llm`
- **方法:** `POST`
- **请求参数:**

```json
{
  "stock_code": "000001"  // 股票代码，必填
}
```

- **响应格式:** `text/plain`
- **响应示例:**

```
# 股票000001分析报告

## 基本情况
- 分析日期: 2023-08-15
- 当前价格: 10.55 元
- 价格变动: 1.23%
- 综合评分: 75分
- 投资建议: 建议买入

## 技术指标分析
- 移动平均线趋势: 上升
- RSI指标: 58.42
- MACD信号: 买入
- 成交量状态: 放量

## AI深度分析
详细的AI分析内容...

## 综合建议
根据技术指标和AI分析，该股票目前建议买入。该建议基于75分的综合评分，评分考虑了趋势、动量、成交量等多个因素。

- 支撑位与压力位见AI分析部分
- 关键指标: RSI(58.42), 移动平均线(上升), 成交量(放量)
- MACD当前发出买入信号
```

### 4. 市场扫描

批量分析多只股票，返回符合条件的推荐股票。

- **URL:** `/scan`
- **方法:** `POST`
- **请求参数:**

```json
{
  "stock_list": ["000001", "600036", "000651", "600519"],  // 股票代码列表，必填
  "min_score": 60  // 最低评分，选填，默认值为60
}
```

- **响应示例:**

```json
{
  "status": "success",
  "data": [
    {
      "stock_code": "000001",
      "score": 75,
      "recommendation": "建议买入",
      // 其他分析数据...
    },
    {
      "stock_code": "600519",
      "score": 82,
      "recommendation": "强烈推荐买入",
      // 其他分析数据...
    }
  ],
  "count": 2
}
```

### 5. 获取技术指标

获取指定股票的技术指标数据。

- **URL:** `/technical_indicators`
- **方法:** `POST`
- **请求参数:**

```json
{
  "stock_code": "000001",  // 股票代码，必填
  "start_date": "20220101",  // 开始日期，选填，格式YYYYMMDD
  "end_date": "20221231"  // 结束日期，选填，格式YYYYMMDD
}
```

- **响应示例:**

```json
{
  "status": "success",
  "data": [
    {
      "date": "2022-12-25",
      "open": 10.28,
      "close": 10.55,
      "high": 10.67,
      "low": 10.25,
      "volume": 12345678,
      "MA5": 10.42,
      "MA20": 10.35,
      "MA60": 10.28,
      "RSI": 58.42,
      "MACD": 0.0582,
      "Signal": 0.0423,
      "MACD_hist": 0.0159,
      "BB_upper": 11.23,
      "BB_middle": 10.35,
      "BB_lower": 9.47,
      "Volume_MA": 10234567,
      "Volume_Ratio": 1.21,
      "ATR": 0.15,
      "Volatility": 1.42,
      "ROC": 2.35
    },
    // 更多数据...
  ],
  "count": 20
}
```

### 6. 获取AI分析

获取指定股票的AI辅助分析结果。

- **URL:** `/ai_analysis`
- **方法:** `POST`
- **请求参数:**

```json
{
  "stock_code": "000001"  // 股票代码，必填
}
```

- **响应示例:**

```json
{
  "status": "success",
  "data": {
    "stock_code": "000001",
    "analysis": "详细的AI分析内容，包括趋势分析、成交量分析、风险评估、目标价位等..."
  }
}
```

## 错误处理

所有接口在发生错误时都会返回相应的错误信息，HTTP状态码为400或500。

- **示例:**

```json
{
  "status": "error",
  "message": "获取股票数据失败: 无法连接到数据源"
}
```

## 调用示例

### 使用curl

```bash
# 分析单只股票（JSON格式）
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "000001"}'

# 分析单只股票（大模型格式）
curl -X POST http://localhost:5000/api/analyze_for_llm \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "000001"}'

# 市场扫描
curl -X POST http://localhost:5000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"stock_list": ["000001", "600036", "000651", "600519"], "min_score": 70}'
```

### 使用Python

```python
import requests
import json

# 服务器地址
base_url = "http://localhost:5000/api"

# 分析单只股票（JSON格式）
def analyze_stock(stock_code):
    response = requests.post(
        f"{base_url}/analyze",
        json={"stock_code": stock_code}
    )
    return response.json()

# 分析单只股票（大模型格式）
def analyze_stock_for_llm(stock_code):
    response = requests.post(
        f"{base_url}/analyze_for_llm",
        json={"stock_code": stock_code}
    )
    return response.text  # 注意这里返回文本而非JSON

# 市场扫描
def scan_market(stock_list, min_score=60):
    response = requests.post(
        f"{base_url}/scan",
        json={"stock_list": stock_list, "min_score": min_score}
    )
    return response.json()

# 示例调用
result = analyze_stock("000001")
print(json.dumps(result, indent=2, ensure_ascii=False))

# 获取大模型格式的分析
llm_text = analyze_stock_for_llm("000001")
print(llm_text)
``` 