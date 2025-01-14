# v9.1.18
FROM squidfunk/mkdocs-material@sha256:ba73db5ab937632760a59742ba89e199ca6122cfad4ca21d1f27125fefa31a33
# pip-compile --generate-hashes --output-file=requirements.txt requirements.in
COPY requirements.txt /tmp/
RUN pip install --require-hashes -r /tmp/requirements.txt
