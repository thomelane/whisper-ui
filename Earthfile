VERSION 0.6
FROM python:3.10-slim
WORKDIR /app

requirements:
    RUN --mount=type=cache,id=pip,target=/root/.cache/pip pip install pip-tools
    COPY requirements.in dev.requirements.in .
    COPY ./whisper ./whisper
    RUN --mount=type=cache,id=pip,target=/root/.cache/pip \
        pip-compile --resolver=backtracking --verbose -o requirements.txt requirements.in && \
        pip-compile --resolver=backtracking --verbose -o dev.requirements.txt dev.requirements.in
    SAVE ARTIFACT requirements.txt AS LOCAL requirements.txt
    SAVE ARTIFACT dev.requirements.txt AS LOCAL dev.requirements.txt

ffmpeg:
    RUN --mount=type=cache,id=apt,target=/var/cache/apt/archives apt-get update && \
        apt-get install --no-install-recommends -y \
        ffmpeg

build:
    FROM +ffmpeg
    COPY +requirements/requirements.txt .
    COPY ./whisper ./whisper
    RUN --mount=type=cache,target=/root/.cache/pip pip install --verbose --requirement requirements.txt
    COPY app.py .
    COPY .streamlit/ .
    EXPOSE 8501
    ENTRYPOINT ["streamlit", "run", "app.py"]
    SAVE IMAGE --push thomelane/whisper-ui:latest

build-all-platforms:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +build

run:
    FROM +build
    LOCALLY
    RUN docker run -p 8501:8501 -v `pwd`/models:/app/models thomelane/whisper-ui:latest

dev-env:
    FROM +ffmpeg
    # using --mount=type=cache to have a build time cache for apt
    # but cache folder is unmounted after this step so
    # copying via to tmp to include the cache in the final image
    RUN --mount=type=cache,id=apt,target=/var/cache/apt/archives apt-get update && \
        apt-get install --no-install-recommends -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \ 
        git
    # Install Docker CLI
    RUN mkdir -p /etc/apt/keyrings
    RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    RUN echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    RUN --mount=type=cache,id=apt,target=/var/cache/apt/archives apt-get update && \
        apt-get install --no-install-recommends -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    # Install Earthly
    RUN curl -fsSL https://pkg.earthly.dev/earthly.pgp | gpg --dearmor -o /usr/share/keyrings/earthly-archive-keyring.gpg
    RUN echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/earthly-archive-keyring.gpg] https://pkg.earthly.dev/deb \
    stable main" | tee /etc/apt/sources.list.d/earthly.list > /dev/null
    RUN --mount=type=cache,id=apt,target=/var/cache/apt/archives apt-get update && \
        apt-get install --no-install-recommends -y earthly
    # Keep apt cache    
    RUN --mount=type=cache,id=apt,target=/var/cache/apt/archives cp -r /var/cache/apt/archives /root/tmp
    RUN mv /root/tmp /var/cache/apt/archives
    # Install Python dev.requirements (which include main requirements too)
    COPY +requirements/dev.requirements.txt .
    COPY ./whisper ./whisper
    # using --mount=type=cache to have a build time cache for pip
    # but cache folder is unmounted after this step so
    # copying via to tmp to include the cache in the final image
    RUN --mount=type=cache,id=pip,target=/root/.cache/pip \
        pip install --verbose \
        --cache-dir /root/.cache/pip \
        --requirement dev.requirements.txt
    # Keep pip cache
    RUN --mount=type=cache,id=pip,target=/root/.cache/pip cp -r /root/.cache/pip /root/tmp
    RUN mv /root/tmp /root/.cache/pip
    SAVE IMAGE thomelane/whisper-ui:devcontainer

dev-run:
    FROM +dev-env
    LOCALLY
    RUN streamlit run app.py