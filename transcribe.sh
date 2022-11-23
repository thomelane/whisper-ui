# Used to transcribe an input video (or audio) file to text.

# Call transcribe.sh with an input_file
# optionally provide a text-prompt to give the model more context about the audio it will listen to

# Usage: transcribe.sh input_file [--text-prompt text_prompt]

set -e

# validate correct number of input arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: transcribe.sh input_video_file [--fast-dev-run] [--text-prompt text_prompt]"
    exit 1
fi

# validate that the input file exists
if [ ! -f $1 ]; then
    echo "input video file does not exist"
    exit 1
fi

INPUT_FOLDER=$(dirname $1)
INPUT_FOLDER_ABSOLUTE=$(cd $INPUT_FOLDER; pwd)
INPUT_BASENAME=$(basename $1)

# check for the --text-prompt flag in any position, and set the text prompt variable
TEXT_PROMPT=""
if [[ "$@" == *"--text-prompt"* ]]; then
    TEXT_PROMPT=$(echo "$@" | sed -n -e 's/.*--text-prompt //p')
fi
echo $TEXT_PROMPT

# transcribe
docker run \
    --rm \
    -v "$INPUT_FOLDER_ABSOLUTE:/data" \
    transcriber \
    python /app/src/transcribe.py /data/$INPUT_BASENAME --text-prompt "$TEXT_PROMPT" # --fast-dev-run
