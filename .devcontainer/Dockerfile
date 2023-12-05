FROM quay.io/fedora/fedora:37

ARG POETRY_VERSION=1.5.1

RUN dnf -y update && \
    yum -y reinstall shadow-utils && \
    yum install -y git \
                   python3 \
                   python3-pip \
                   python3-devel \
                   gcc-c++ && \
    rm -rf /var/cache /var/log/dnf* /var/log/yum.*

RUN useradd -u 1000 trestlebot

ENV HOME=/home/trestlebot
ENV PYSETUP_PATH="$HOME/trestle-bot" \
    VENV_PATH="$HOME/trestle-bot/.venv"

RUN mkdir -p "$PYSETUP_PATH"

# Installing poetry and pipx.
RUN python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir pipx \
    && python3 -m pipx install poetry=="$POETRY_VERSION"

# set permissions
RUN chown trestlebot:trestlebot -R /home/trestlebot

USER trestlebot