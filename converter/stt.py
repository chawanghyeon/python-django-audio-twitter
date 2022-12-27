import whisper

model = whisper.load_model("large")

# # load audio and pad/trim it to fit 30 seconds
# audio = whisper.load_audio("done.wav")
# audio = whisper.pad_or_trim(audio)

# # make log-Mel spectrogram and move to the same device as the model
# mel = whisper.log_mel_spectrogram(audio).to(model.device)

# # detect the spoken language
# _, probs = model.detect_language(mel)
# print(f"Detected language: {max(probs, key=probs.get)}")

# # decode the audio
# options = whisper.DecodingOptions()
# result = whisper.decode(model, mel, options)

# # print the recognized text
# print(result.text)

result = model.transcribe("test.mp3")
print(result["text"])

from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline

model_name = "monologg/koelectra-base-finetuned-nsmc"
tokenizer = ElectraTokenizer.from_pretrained(model_name)
model = ElectraForSequenceClassification.from_pretrained(model_name)

nsmc = pipeline(
    "sentiment-analysis",
    tokenizer=tokenizer,
    model=model
)

print(nsmc("이 영화는 미쳤다. 넷플릭스가 일상화된 시대에 극장이 존재해야하는 이유를 증명해준다."))
print(nsmc("와 진짜 너무 재미없네요는 뻥이고 진짜 너무 재밌어요"))
print(nsmc(result["text"]))