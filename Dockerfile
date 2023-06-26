FROM registry.access.redhat.com/ubi8/python-38 AS demo

COPY ./ /trestle-bot

WORKDIR /trestle-bot

# Install dependencies
RUN  python3.8 -m pip install --upgrade pip \
     && pip install poetry \ 
     && poetry install
USER 1001
ENTRYPOINT [ "poetry", "run", "trestle-bot" ] 
