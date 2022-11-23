# Whisper

## Pre-requisites

Docker

## Usage

```bash
bash ./build.sh
bash ./transcribe ./data/example.mp4
ls ./data
```

### Options

#### Change the model size

```bash
bash ./build.sh medium.en
```

A larger model typically gives better transcription accuracy, but it will take more storage/memory and take longer to transcribe. Option are `tiny.en`, `small.en`, `medium.en`, `large.en`: and default was set to `small.en`.

#### Give a text prompt

When transcribing audio, it's sometimes beneficial to give the model more context about the audio it's listening to. With `data/example.mp4` as an example, you can give the model a text prompt like so:

```bash
bash ./transcribe.sh ./data/example.mp4 --text-prompt "A YouTube video about OpenAI's new model: "
```

So the model is more likely to transcribe "OpenAI" instead of "Open a eye".

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
