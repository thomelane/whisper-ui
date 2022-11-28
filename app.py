import datetime
import io
import shutil
import tempfile

import ffmpeg
import streamlit as st
import whisper


@st.cache
def get_whisper_model(model_name: str) -> whisper.Whisper:
    with st.spinner(text="Getting Model"):
        model = whisper.load_model(model_name, download_root="./models")
    return model


def extract_audio(input_bytes: io.BytesIO) -> io.BytesIO:
    with st.spinner(text="Extracting Audio"):
        start_time = datetime.datetime.now()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = f"{tmpdir}/input.mp4"
            output_file = f"{tmpdir}/output.mp3"
            with open(input_file, 'wb') as f:
                f.write(input_bytes.read())
            stream = ffmpeg.input(input_file)
            ffmpeg.output(stream.audio, output_file).run()
            with open(output_file, 'rb') as f:
                output_bytes = io.BytesIO(f.read())
        end_time = datetime.datetime.now()
        st.success(f"Audio extracted in {str(end_time - start_time).split('.')[0]}.")
    return output_bytes


def apply_model(model: whisper.Whisper, audio_bytes: io.BytesIO, text_prompt: str = None):
    with st.spinner(text="Transcribing Audio"):
        start_time = datetime.datetime.now()
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = f"{tmpdir}/input.mp3"
            with open(input_file, 'wb') as f:
                f.write(audio_bytes.read())
            results = model.transcribe(
                input_file,
                fp16=False,
                initial_prompt=text_prompt
            )
        end_time = datetime.datetime.now()
        st.success(f"Audio transcribed in {str(end_time - start_time).split('.')[0]}.")
    return results


def format_timed_transcription(results: dict) -> io.StringIO:
    lines = []
    for segment in results["segments"]:
        start_seconds = segment["start"]
        # convert start_seconds to string in HH:MM:SS format
        start_time = str(datetime.timedelta(seconds=round(start_seconds))).split(".")[0]
        # format text
        text = segment["text"].strip()
        lines.append(f"[{start_time}] {text}")
    st.text_area("Sample Transcription", "\n".join(lines[:10]), height=250)
    # create single string
    output_str = "\r\n".join(lines)
    output_file = io.BytesIO()
    output_file.write(output_str.encode())
    return output_file


def make_archive(audio: io.BytesIO, transcript: io.BytesIO) -> io.BytesIO:
    with st.spinner(text="Creating Archive"):
        with tempfile.TemporaryDirectory() as compressed:
            with tempfile.TemporaryDirectory() as uncompressed:
                with open(f"{uncompressed}/input.mp3", 'wb') as f:
                    # reset file pointer to beginning of file
                    audio.seek(0)
                    f.write(audio.read())
                with open(f"{uncompressed}/transcript.txt", 'wb') as f:
                    transcript.seek(0)
                    f.write(transcript.read())
                archive_basename = f"{compressed}/archive"
                # zip all the files in the uncompressed directory
                shutil.make_archive(archive_basename, 'zip', uncompressed)
            # read the zip file into a BytesIO object
            with open(f"{archive_basename}.zip", 'rb') as f:
                archive_bytes = io.BytesIO(f.read())
    return archive_bytes


def transcribe(model_name: str, input_file: io.BytesIO, initial_prompt: str):
    if uploaded_file is None:
        st.error('Error: Choose a file to transcribe.')
        return
    st.header('Progress')
    model = get_whisper_model(model_name)
    audio = extract_audio(input_file)
    results = apply_model(model, audio, initial_prompt)
    st.header('Outputs')
    timed_transcription = format_timed_transcription(results)
    archive = make_archive(audio, timed_transcription)
    st.download_button(
        "Download", archive,
        file_name=f'archive.zip', mime='application/zip'
    )
    st.balloons()

st.title('Whisper Audio Transcriber')

st.header('Model')

model_name = st.selectbox(
    label='Select Whisper model (`*.en` models are English specific):',
    options=['tiny', 'tiny.en', 'base', 'base.en', 'small', 'small.en', 'medium', 'medium.en', 'large'],
    index=1
)

st.header('Inputs')

uploaded_file = st.file_uploader("Choose a file to transcribe:")

initial_prompt = st.text_input('Optionally, enter an initial prompt for the model. Otherwise leave blank.')
st.caption("""
An initial prompt can be used to give the model context about the audio it is about to hear. "A YouTube video about OpenAI:" could help the model decide between "open a eye" and "OpenAI" when transcribing. "A meeting recording discussing the YGI-2020 project: " could help the model correctly transcribe the project name or "A podcast about internet protocols:" could help the model transcribe protocols abbreviations correctly (e.g. HTTPS).
""")

st.header('Controls')

button = st.button('Start')
if button:
    transcribe(model_name, uploaded_file, initial_prompt)
