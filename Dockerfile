FROM registry.access.redhat.com/ubi8/python-38 AS demo

COPY ./ /trestle-bot

WORKDIR /trestle-bot

USER root

# Install dependencies
RUN  python3.8 -m pip install --upgrade pipx \
     && pipx install poetry==1.5.1 \
     && poetry config virtualenvs.create false \
     && poetry install --without tests,dev

RUN  chown -HR 1001:1001 /trestle-bot \
     chown -HR 1001:1001 /opt/app-root/src/
     
USER 1001

ENTRYPOINT poetry run trestle-bot \
           --markdown-path="${MARKDOWN_PATH}" \
           --assemble-model="${ASSEMBLE_MODEL}" \
           --ssp-index-path="${SSP_INDEX_PATH}" \
           --commit-message="${COMMIT_MESSAGE}" \
           --branch="${BRANCH}" \
           --patterns="${PATTERNS}" \
           --committer-name="${COMMIT_USER_NAME}" \
           --committer-email="${COMMIT_USER_EMAIL}" \
           --author-name="${AUTHOR_NAME}" \
           --author-email="${AUTHOR_EMAIL}" \
           --working-dir="${WORKING_DIR}"
