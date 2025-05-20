FROM python:3.9-slim

WORKDIR /app

# 复制所需文件
COPY requirements.txt ./
COPY stock_analyzer.py ./
COPY app.py ./
COPY .env ./

# 复制静态文件
COPY static/ ./static/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV HOST=0.0.0.0
ENV PORT=5000

# 启动命令
CMD ["python", "app.py"] 