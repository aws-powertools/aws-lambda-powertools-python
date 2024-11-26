# v9.1.18
FROM squidfunk/mkdocs-material@sha256:ef0b45e758c46f02e1d7c9662435e2de6de143c61eb1af1deec24c22ec79649b
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
