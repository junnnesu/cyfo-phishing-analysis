FROM python:3.9-slim

# 安装必要工具
RUN apt-get update && apt-get install -y \
    unzip \
    file \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /forensics

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制分析脚本
COPY analyze_emails.py .
