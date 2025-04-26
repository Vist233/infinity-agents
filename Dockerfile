# 使用官方 Python 3.10 镜像作为基础
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY . .

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["python", "app/app.py"]