import whisper

def transcribe_audio(file, model_str):
    model = whisper.load_model(model_str)
    result = model.transcribe(file)
    return result