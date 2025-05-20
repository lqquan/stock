# 股票分析器 API 服务部署指南

本文档介绍如何部署和运行股票分析器API服务。

## 1. 直接在服务器上运行

### 前提条件

- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. 克隆或下载代码到服务器
   ```bash
   git clone <repository-url>
   cd stock-analyzer
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 创建并配置环境变量文件（.env）
   ```bash
   # 创建.env文件
   touch .env
   
   # 编辑.env文件，添加以下内容
   GEMINI_API_KEY=your_gemini_api_key_here
   PORT=5000
   HOST=0.0.0.0
   ```

4. 启动服务
   ```bash
   python app.py
   ```

5. 验证服务
   ```bash
   curl http://localhost:5000/api/health
   ```

### 使用Supervisor管理进程（推荐）

可以使用Supervisor来管理API服务进程，确保服务持续运行。

1. 安装Supervisor
   ```bash
   apt-get update
   apt-get install supervisor
   ```

2. 创建配置文件
   ```bash
   # 创建配置文件
   sudo nano /etc/supervisor/conf.d/stock-analyzer.conf
   ```

3. 添加以下配置
   ```ini
   [program:stock-analyzer]
   command=python /path/to/stock-analyzer/app.py
   directory=/path/to/stock-analyzer
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/stock-analyzer.err.log
   stdout_logfile=/var/log/stock-analyzer.out.log
   user=your_username
   environment=PATH="/usr/local/bin"
   ```

4. 更新Supervisor配置并启动服务
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start stock-analyzer
   ```

## 2. 使用Docker部署

### 前提条件

- Docker 安装在服务器上
- Docker Compose (可选)

### 构建和运行Docker镜像

1. 构建Docker镜像
   ```bash
   docker build -t stock-analyzer:latest .
   ```

2. 创建.env文件（如果没有）
   ```bash
   # 创建.env文件
   touch .env
   
   # 编辑.env文件，添加以下内容
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. 运行Docker容器
   ```bash
   docker run -d -p 5000:5000 --env-file .env --name stock-analyzer stock-analyzer:latest
   ```

4. 验证服务
   ```bash
   curl http://localhost:5000/api/health
   ```

### 使用Docker Compose（可选）

1. 创建docker-compose.yml文件
   ```yaml
   version: '3'
   services:
     stock-analyzer:
       build: .
       ports:
         - "5000:5000"
       env_file:
         - .env
       restart: always
   ```

2. 启动服务
   ```bash
   docker-compose up -d
   ```

## 3. 使用Nginx作为反向代理

如果需要将API服务暴露到公网，建议使用Nginx作为反向代理。

### Nginx配置示例

1. 安装Nginx
   ```bash
   apt-get update
   apt-get install nginx
   ```

2. 创建Nginx配置文件
   ```bash
   sudo nano /etc/nginx/sites-available/stock-analyzer
   ```

3. 添加以下配置
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;
       
       location /api {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

4. 启用配置并重启Nginx
   ```bash
   sudo ln -s /etc/nginx/sites-available/stock-analyzer /etc/nginx/sites-enabled/
   sudo nginx -t  # 测试配置是否有效
   sudo systemctl restart nginx
   ```

## 4. 安全注意事项

- 添加API密钥认证（目前版本未实现）
- 限制API访问频率
- 始终使用HTTPS进行加密通信
- 定期更新依赖库以修复安全漏洞

## 5. 监控和日志

### 查看日志

- 直接运行时的日志：直接在控制台可见
- Supervisor管理时的日志：`/var/log/stock-analyzer.out.log`和`/var/log/stock-analyzer.err.log`
- Docker容器日志：`docker logs stock-analyzer`

### 监控

可以使用以下工具进行服务监控：

- Prometheus + Grafana（适合大规模部署）
- 简单的状态监控脚本（定期检查`/api/health`端点）

## 6. 故障排除

### 常见问题

1. 服务无法启动
   - 检查依赖是否正确安装：`pip list`
   - 检查环境变量是否正确设置
   - 检查端口是否被占用：`netstat -tulpn | grep 5000`

2. API返回错误
   - 检查日志文件以获取详细错误信息
   - 确认请求格式是否正确
   - 验证数据源是否可用（如akshare能否正常获取数据）

3. Docker容器异常退出
   - 查看Docker日志：`docker logs stock-analyzer`
   - 检查.env文件是否被正确挂载
   - 确认所有依赖都已在Dockerfile中安装

## 7. 联系与支持

如果遇到问题或需要支持，请联系：

- 邮箱：your_email@example.com
- 项目仓库：<repository-url> 