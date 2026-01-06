
FROM ubuntu:24.04 AS builder

ENV LANG=en_US.UTF-8
RUN apt-get update -y && apt-get install -y \
    build-essential cmake git gdb lcov libcurl4-openssl-dev ninja-build

WORKDIR /workspace
RUN git clone https://github.com/r-tooling/r4r.git .
RUN BUILD_TYPE=Release make clean install


FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=en_US.UTF-8 \
    TZ=Etc/UTC

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends locales tzdata && \
    locale-gen $LANG && \
    update-locale LANG=$LANG

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl lsb-release git gnupg2 gosu lz4 \
    nano time less sudo python3 python3-pip python3-venv \
    && mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y --no-install-recommends docker-ce-cli

RUN apt-get update -y && apt-get -y install \
    pandoc r-base r-base-dev r-recommended \
    libeigen3-dev libfontconfig1-dev libssl-dev libx11-dev \
    libcurl4-openssl-dev zlib1g-dev libfreetype6-dev libjpeg-dev \
    libpng-dev libtiff-dev libxml2-dev libfribidi-dev libharfbuzz-dev \
    libicu-dev pari-gp cmake make libglpk-dev libcairo2-dev \
    libproj-dev libgdal-dev gdal-bin libgeos-dev libsqlite3-dev \
    libudunits2-dev libmagick++-dev gsfonts unixodbc-dev \
    linux-libc-dev libgmp3-dev libmpfr-dev 


RUN apt-get update && apt-get install -y \
    libopencv-dev libtirpc-dev \
    && rm -rf /var/lib/apt/lists/* 
RUN R -e "install.packages('rmarkdown', repos='https://cran.rstudio.com/')"

RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

COPY --from=builder /usr/local/bin/r4r /usr/local/bin/r4r
COPY libs/* /usr/local/lib/
RUN ldconfig
COPY rdiff /usr/local/bin/r-diff
RUN chmod +x /usr/local/bin/r-diff

RUN r-diff --help

ARG USERNAME=r4r
ARG USER_UID=1001
ARG USER_GID=1001

RUN groupadd -g $USER_GID $USERNAME && \
    useradd -u $USER_UID -g $USERNAME -m -s /bin/bash $USERNAME && \
    groupadd -f docker && \
    usermod -aG docker $USERNAME && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

RUN gosu r4r R -e 'dir.create(unlist(strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep))[1L], recursive=TRUE)'    
WORKDIR /app



RUN python3 -m venv /opt/venv && \
    chown -R $USERNAME:$USERNAME /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/storage/notebooks && \
    chown -R $USERNAME:$USERNAME /app/storage


COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]