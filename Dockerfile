# 1. 使用 Ubuntu 基础镜像
FROM ubuntu:20.04

# Set the timezone non-interactively
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    echo "Etc/UTC" > /etc/timezone

# 2. 安装基本依赖
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    libglib2.0-0 \
    libx11-6 \
    libxext6 \
    libsm6 \
    libxi6 \
    perl \
    && apt-get clean

# 3. 安装 Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm -rf /tmp/miniconda.sh

# 4. 设置环境变量：将 Conda 和 Python 路径添加到环境变量中
ENV PATH="/opt/conda/bin:$PATH"
ENV CONDA_DEFAULT_ENV=base
COPY Bioinfomatics-Software/CPJSdraw-main/bin/CPJSdraw.pl /usr/local/bin/
COPY Bioinfomatics-Software/Kaks_Calculator-main/kaks_slidingwindow.pl /usr/local/bin/
COPY Bioinfomatics-Software/misa/misa.pl /usr/local/bin/
COPY Bioinfomatics-Software/misa/misa.ini /usr/local/bin/

# 5. 创建 Conda 环境并安装 Python 3.10
RUN conda config --set solver classic && \
    conda update -n base -c defaults conda && \
    conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda install python=3.10 -y && \
    conda install -y raxml-ng modeltest mafft CPSTools vcftools gatk samtools bwa snpeff pyinstaller

# 6. 复制 requirements.txt 文件到容器中
COPY requirements.txt /tmp/requirements.txt

# 7. 安装 Python 依赖
RUN conda run -n base pip install -r /tmp/requirements.txt

# 8. 设置工作目录
WORKDIR /app

# 9. 复制应用程序的代码
COPY . .

# 10. 确保每次运行时都在 `base` 环境中
#     启动时默认使用 /bin/bash，激活 `base` 环境。
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "base", "bash"]

# 11. 暴露应用所需的端口（根据实际情况设置）
EXPOSE 8080

# 12. 设置容器启动命令
# CMD ["python", "main.py"]  # 替换为你实际的启动命令