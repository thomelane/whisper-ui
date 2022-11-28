# Whisper

## Pre-requisites

* Docker
* Earthly

## Usage

```bash
earthly +run
# or equivalently
docker run -d -p 8501:8501 -v `pwd`/models:/app/models thomelane/whisper-ui:latest
```

## Development

```
earthly +dev-env
# Open VS Code with 'Rebuild and Reopen in Container'
```

🛑 'Rebuild' from VS Code doesn't rebuild the image, it just makes sure the *latest* image is being used.
Use `earthly +dev-env` to actually rebuild the container. Can even be called from inside the dev container!

## References

* Official implementation found at https://github.com/openai/whisper
* Dockerfile based on https://github.com/MatthiasZepper/whisper-dockerized

## Other Notes

### Sampling 30 seconds of a random YouTube video

```bash
apt-get -qq update
apt-get -qq install curl
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
chmod a+rx /usr/local/bin/yt-dlp
yt-dlp -f 18 -o ./data/example_full.mp4 "https://www.youtube.com/watch?v=uFOkMme19Zs"
# extract the first minute of the video
ffmpeg -i data/example_full.mp4 -t 00:00:30 -c copy data/example.mp4
rm data/example_full.mp4
```
