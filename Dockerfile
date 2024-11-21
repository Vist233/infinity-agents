# 1. 使用 Ubuntu 22.04 作为基础镜像
FROM ubuntu:22.04

# 2. 设置时区并安装系统依赖
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    echo "Etc/UTC" > /etc/timezone && \
    apt-get update && apt-get install -y --no-install-recommends \
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
        libarchive-dev && \
    rm -rf /var/lib/apt/lists/*

# 3. 安装 Miniconda 并设置环境变量
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    /opt/conda/bin/conda clean -afy
ENV PATH="/opt/conda/bin:$PATH"
ENV CONDA_DEFAULT_ENV=base

# 4. 复制生物信息学工具
COPY Bioinfomatics-Software/CPJSdraw-main/bin/CPJSdraw.pl \
     Bioinfomatics-Software/Kaks_Calculator-main/kaks_slidingwindow.pl \
     Bioinfomatics-Software/misa/misa.pl \
     Bioinfomatics-Software/misa/misa.ini \
     /usr/local/bin/

# 5. 配置 Conda 并安装依赖
RUN conda install -y mamba -n base -c conda-forge && \
    conda config --set solver libmamba && \
    conda update -n base -c defaults conda && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    mamba install -y python=3.10 \
        raxml-ng \
        modeltest-ng \
        mafft \
        CPSTools \
        vcftools \
        gatk \
        samtools \
        bwa \
        snpeff \
        pyinstaller && \
    conda clean -afy

# 6. 安装 Python 依赖
COPY requirements.txt /tmp/requirements.txt
RUN conda init bash && \
    /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    pip install --no-cache-dir --upgrade setuptools && \
    pip install --no-cache-dir -r /tmp/requirements.txt" && \
    rm /tmp/requirements.txt

# 7. 设置应用工作目录并复制文件
WORKDIR /app
COPY . .

# 8. 配置容器运行时
EXPOSE 8080
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "base", "bash"]

# 可选：根据您的应用取消注释并修改 CMD
# CMD ["python", "main.py"]