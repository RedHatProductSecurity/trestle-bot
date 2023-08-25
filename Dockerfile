# kics-scan disable=fd54f200-402c-4333-a5a4-36ef6709af2f,b03a748a-542d-44f4-bb86-9199ab4fd2d5
FROM python:3.9-slim as python-base

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

FROM python-base as dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for building python deps
        build-essential \
        git

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN  python3.9 -m pip install --no-cache-dir --upgrade pip \
     && pip install --no-cache-dir poetry=="$POETRY_VERSION"

# Cache runtime deps
WORKDIR $PYSETUP_PATH
COPY ./ $PYSETUP

RUN poetry install --without tests,dev

# final image
FROM python-base as final

COPY --from=dependencies $PYSETUP_PATH $PYSETUP_PATH

RUN apt-get update \
    && apt-get install --no-install-recommends -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["python3.9", "-m" , "trestlebot"]
           
