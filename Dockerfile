# 使用 Ubuntu 24.04 作为基础镜像
FROM ubuntu:24.04

# 设置工作目录
WORKDIR /app

# 配置国内镜像源（阿里云）以提升下载速度和稳定性
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.aliyun.com@g' /etc/apt/sources.list.d/ubuntu.sources

# 安装系统依赖和 Python
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv（使用 --break-system-packages 或使用 pipx）
RUN apt-get install -y pipx && pipx install uv && ln -s /root/.local/bin/uv /usr/local/bin/uv || pip install --break-system-packages --no-cache-dir uv

# 复制项目文件（包括 .env，不包括 .venv）
COPY rag-backend/ /app/rag-backend/

# 切换到后端项目目录
WORKDIR /app/rag-backend

# 创建虚拟环境并同步依赖
RUN uv sync

# 暴露 FastAPI 默认端口
EXPOSE 8000

# 设置基础环境变量
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/rag-backend/.venv/bin:$PATH"

# 使用项目的虚拟环境运行 main.py
CMD [".venv/bin/python", "main.py"]
