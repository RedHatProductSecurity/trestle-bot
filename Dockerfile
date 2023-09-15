# Use the UBI 8 minimal base image
FROM registry.access.redhat.com/ubi8/ubi-minimal:latest as python-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.5.1 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/trestle-bot" \
    VENV_PATH="/trestle-bot/.venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN microdnf update -y \
    && microdnf install -y python3.9 \
    && microdnf clean all \
    && rm -rf /var/lib/apt/lists/*

FROM python-base as dependencies

RUN microdnf update -y \
    && microdnf install -y git

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN  python3.9 -m pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry=="$POETRY_VERSION"

# Cache runtime deps
WORKDIR "/build"
COPY . "/build"

# Install runtime deps
RUN python -m venv $VENV_PATH && \
  . $VENV_PATH/bin/activate && \
  poetry install --without tests,dev --no-root

# install the root project in non-editable mode
RUN . $VENV_PATH/bin/activate && \
  poetry build -f wheel -n && \
  pip install --no-cache-dir --no-deps dist/*.whl && \
  rm -rf dist *.egg-info

# final image
FROM python-base as final

COPY --from=dependencies $PYSETUP_PATH $PYSETUP_PATH

RUN microdnf install -y git \
    && microdnf clean all \
    && rm -rf /var/lib/apt/lists/*

COPY ./actions/autosync/auto-sync-entrypoint.sh /
RUN chmod +x /auto-sync-entrypoint.sh

COPY ./actions/rules-transform/rules-transform-entrypoint.sh /
RUN chmod +x /rules-transform-entrypoint.sh

ENTRYPOINT ["python3.9", "-m" , "trestlebot"]
CMD ["--help"]
           
