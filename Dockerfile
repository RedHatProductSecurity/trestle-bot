# Use the UBI 8 minimal base image
# kics-scan disable=fd54f200-402c-4333-a5a4-36ef6709af2f
FROM registry.access.redhat.com/ubi8/ubi-minimal:latest AS python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Paths for the virtual environment and working directory
    PYSETUP_PATH="/trestle-bot" \
    VENV_PATH="/trestle-bot/.venv"

LABEL maintainer="Red Hat Product Security" \
      summary="Trestle Bot"

# Ensure we use the virtualenv
ENV PATH="$VENV_PATH/bin:$PATH"

RUN microdnf update -y \
    && microdnf install -y python3.9 git \
    && microdnf clean all \
    && rm -rf /var/lib/apt/lists/*

FROM python-base AS dependencies

ARG POETRY_VERSION=1.5.1

# https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

# install poetry - respects $POETRY_HOME
RUN  python3.9 -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry=="$POETRY_VERSION"

WORKDIR "/build"
COPY . "/build"

# Install runtime deps and install the project in non-editable mode.
RUN python3.9 -m venv "$VENV_PATH" && \
  . "$VENV_PATH"/bin/activate && \
  poetry install --without tests,dev --no-root && \
  poetry build -f wheel -n && \
  pip install --no-cache-dir --no-deps dist/*.whl && \
  rm -rf dist ./*.egg-info


FROM python-base AS final

COPY --from=dependencies $PYSETUP_PATH $PYSETUP_PATH

# Add wrappers for entrypoints that provide support for the actions
COPY ./actions/autosync/auto-sync-entrypoint.sh /
COPY ./actions/rules-transform/rules-transform-entrypoint.sh /
COPY ./actions/create-cd/create-cd-entrypoint.sh /
RUN chmod +x /auto-sync-entrypoint.sh /rules-transform-entrypoint.sh /create-cd-entrypoint.sh

ENTRYPOINT ["python3.9", "-m" , "trestlebot"]
CMD ["--help"]
