# 股票分析器

一个基于Python的股票分析工具，结合了技术分析和AI辅助分析，帮助投资者做出更明智的投资决策。

## 功能特点

- **技术指标分析**：计算并分析多种技术指标（MA、RSI、MACD、布林带等）
- **智能评分系统**：根据技术指标综合评分，提供投资建议
- **AI 辅助分析**：利用Gemini AI进行深度市场分析
- **市场扫描**：批量分析多只股票，寻找投资机会
- **数据可视化**：生成直观的分析报告
- **API服务**：提供RESTful API接口，支持与其他应用集成

## 安装说明

### 前提条件

- Python 3.8 或更高版本
- 必要的Python库（见下方requirements.txt）

### 安装步骤

1. 克隆或下载本项目到本地
   ```
   git clone <repository-url>
   ```
   
2. 安装所需的Python库
   ```
   pip install -r requirements.txt
   ```
   
3. 创建 `.env` 文件，并设置您的Gemini API密钥
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## 使用方法

### 本地分析

#### 分析单只股票

```python
from stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()
report = analyzer.analyze_stock("000001")  # 分析平安银行
print(report)
```

#### 市场扫描

```python
from stock_analyzer import StockAnalyzer

analyzer = StockAnalyzer()
stock_list = ["000001", "600036", "000651", "600519", "000333"]
recommendations = analyzer.scan_market(stock_list, min_score=60)
print(recommendations)
```

#### 运行主程序

直接运行 `main.py` 文件，将执行默认的分析流程：

```
python main.py
```

### 作为API服务运行

你可以将股票分析器作为API服务运行，使其他应用能够通过HTTP请求获取分析结果。

1. 启动API服务
   ```
   python app.py
   ```

2. 服务将在 http://localhost:5000 上运行，提供以下API端点：
   - `/api/health` - 健康检查
   - `/api/analyze` - 分析单只股票
   - `/api/scan` - 市场扫描
   - `/api/technical_indicators` - 获取技术指标
   - `/api/ai_analysis` - 获取AI分析

详细的API文档可参见 `API_DOCS.md`。

### 使用Docker部署

我们提供了Docker支持，便于快速部署：

```bash
# 构建镜像
docker build -t stock-analyzer .

# 运行容器
docker run -p 5000:5000 --env-file .env stock-analyzer
```

或者使用Docker Compose:

```bash
docker-compose up -d
```

## 配置参数

您可以根据自己的需求调整技术指标参数：

```python
analyzer = StockAnalyzer()
analyzer.params = {
    'ma_periods': {'short': 5, 'medium': 20, 'long': 60},
    'rsi_period': 14,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'volume_ma_period': 20,
    'atr_period': 14
}
```

## API密钥配置

本项目使用Google的Gemini API进行AI辅助分析。您需要：

1. 获取Gemini API密钥: [https://ai.google.dev/](https://ai.google.dev/)
2. 将密钥添加到 `.env` 文件中

## 文件结构

- `stock_analyzer.py` - 核心分析库，包含所有分析功能
- `main.py` - 命令行运行的主程序
- `app.py` - API服务
- `examples.py` - 使用示例
- `client_example.py` - API客户端示例
- `requirements.txt` - 项目依赖
- `API_DOCS.md` - API文档
- `DEPLOYMENT.md` - 部署指南
- `Dockerfile` 和 `docker-compose.yml` - Docker配置文件

## 注意事项

- 本工具仅供参考，不构成投资建议
- 使用前请确保API密钥已正确配置
- 股票分析需要有效的网络连接以获取最新数据

## 依赖库

- pandas
- numpy
- requests
- python-dotenv
- akshare（用于获取中国股票数据）
- flask (用于API服务)
- waitress (用于生产环境部署)
- flask-cors (用于解决跨域请求问题) 