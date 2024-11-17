# 1. Use Ubuntu base image
FROM ubuntu:22.04

# 2. Set timezone non-interactively
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime && \
    echo "Etc/UTC" > /etc/timezone

# 3. Install system dependencies
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
    libarchive-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Miniconda and set environment variables
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm -rf /tmp/miniconda.sh
ENV PATH="/opt/conda/bin:$PATH"
ENV CONDA_DEFAULT_ENV=base

# 5. Copy bioinformatics tools
COPY Bioinfomatics-Software/CPJSdraw-main/bin/CPJSdraw.pl \
     Bioinfomatics-Software/Kaks_Calculator-main/kaks_slidingwindow.pl \
     Bioinfomatics-Software/misa/misa.pl \
     Bioinfomatics-Software/misa/misa.ini \
     /usr/local/bin/

# 6. Configure conda and install dependencies
RUN conda config --set solver classic && \
    conda update -n base -c defaults conda && \
    conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    conda install -y python=3.10 \
    raxml-ng \
    modeltest-ng \
    mafft \
    CPSTools \
    vcftools \
    gatk \
    samtools \
    bwa \
    snpeff \
    pyinstaller

# 7. Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN conda init bash && \
    /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    pip install --upgrade setuptools && \
    pip install -r /tmp/requirements.txt" && \
    rm /tmp/requirements.txt

# 8. Set up application
WORKDIR /app
COPY . .

# 9. Configure container runtime
EXPOSE 8080
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "base", "bash"]

# Optional: Uncomment and modify the CMD based on your application
# CMD ["python", "main.py"]