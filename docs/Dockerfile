# v9.1.18
FROM squidfunk/mkdocs-material@sha256:2c2802b4d26154eb2c30238ba8ed3aab3a6276009334fd99613e4c01e97cd420
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
