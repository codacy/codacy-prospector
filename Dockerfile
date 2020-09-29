FROM python:3.7-slim
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/codacy_prospector.py codacy_prospector.py
COPY src/codacy_prospector_test.py codacy_prospector_test.py
COPY docs /docs
COPY src/default.yml /default.yml
RUN useradd -u 2004 -U docker
RUN mkdir /home/docker
RUN chown -R docker:docker /docs /home/docker
USER docker
ENTRYPOINT [ "python3.7" ]
CMD [ "codacy_prospector.py" ]
