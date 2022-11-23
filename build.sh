# Get MODEL_SIZE from command line
# Set MODEL_SIZE to small.en if not specified
MODEL_SIZE=${1:-small.en}
# Build Docker image (the model will be stored inside the image)
docker build --build-arg MODEL_SIZE=$MODEL_SIZE -t transcriber .