import os
import datetime
from pathlib import Path
import ffmpeg
import whisper


def get_args():
    print("getting arguments")
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="input file")
    parser.add_argument("--fast-dev-run", action="store_true", help="will only transcribe first minute of input_file")
    parser.add_argument("--text-prompt", default=None, help="optional text prompt")
    args = parser.parse_args()
    return args


def validate_args(args):
    print("validating arguments")
    assert Path(args.input_file).is_file(), "input_file must be a file"


def extract_audio(input_file: str, fast_dev_run: bool = False):
    print("extracting audio from input file")
    # check if input file is already an mp3 file
    if input_file.endswith(".mp3"):
        return input_file
    # convert input file to mp3
    # output_file as input_file with extension changed to mp3
    output_file = str(Path(input_file).with_suffix(".mp3"))
    if Path(output_file).is_file():
        os.remove(output_file)
    input_stream = ffmpeg.input(input_file)
    # trim to first 30 seconds of input file if in fast_dev_run mode
    if fast_dev_run:
        audio = input_stream.audio.filter("atrim", start=0, end=30)
    else:
        audio = input_stream.audio
    
    ffmpeg.output(audio, output_file).run()
    return output_file


def transcribe(audio_file: str, text_prompt: str = None):
    print("transcribing audio file")
    model_size = os.getenv("MODEL_SIZE")
    assert model_size
    model = whisper.load_model(model_size)
    print("initial_prompt:", text_prompt)
    results = model.transcribe(
        audio_file,
        fp16=False,
        initial_prompt=text_prompt,
        verbose=True,
    )
    return results


def output_timed_text(input_file: str, results: dict):
    print("outputting timed text file")
    lines = []
    for segment in results["segments"]:
        start_seconds = segment["start"]
        # convert start_seconds to string in HH:MM:SS format
        start_time = str(datetime.timedelta(seconds=round(start_seconds))).split(".")[0]
        # format text
        text = segment["text"].strip()
        lines.append(f"{start_time}: {text}\n")
    # replace sentence enders with newlines
    output_file = str(Path(input_file).with_suffix(".timed.txt"))
    with open(output_file, "w") as f:
        f.writelines(lines)


def output_text(input_file: str, results: dict):
    print("outputting text file")
    text = results["text"]
    # replace sentence enders with newlines
    formatted_text = text.replace(". ", ".\n").strip()
    output_file = str(Path(input_file).with_suffix(".txt"))
    with open(output_file, "w") as f:
        f.write(formatted_text)


if __name__ == '__main__':
    args = get_args()
    validate_args(args)
    audio_file = extract_audio(args.input_file, fast_dev_run=args.fast_dev_run)
    transcription = transcribe(audio_file, text_prompt=args.text_prompt)
    output_text(args.input_file, transcription)
    output_timed_text(args.input_file, transcription)
