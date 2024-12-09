# v9.1.18
FROM squidfunk/mkdocs-material@sha256:d485eb6e9ca02fa8158311e55595c344eb01db5587a7b2c35560c13cb906e3cd
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
