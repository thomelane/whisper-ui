FROM python:3.9.9-slim

RUN apt-get -qq update
RUN apt-get -qq install --no-install-recommends ffmpeg
RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir "poetry>=1.2.0"

# set work directory to /app
WORKDIR /app
# copy pyproject.toml into /app
COPY pyproject.toml .

RUN poetry config virtualenvs.create false && poetry lock
RUN poetry install --only main --no-root

# Create ARG called MODEL_SIZE
ARG MODEL_SIZE
ENV MODEL_SIZE=$MODEL_SIZE
# copy download.py and download model of MODEL_SIZE
COPY src/download.py /app/src/download.py
RUN python /app/src/download.py

# copy transcribe.py
COPY src/transcribe.py /app/src/transcribe.py