import os
import whisper


if __name__ == '__main__':
    model_name = os.getenv("MODEL_SIZE")
    assert model_name
    model = whisper.load_model(model_name)
