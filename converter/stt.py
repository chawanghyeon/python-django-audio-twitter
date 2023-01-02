from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
import whisper

whisper_model = whisper.load_model("small", device="cpu")
stt = whisper_model.transcribe("test.mp3", fp16=False)

model_name = "monologg/koelectra-base-finetuned-nsmc"
tokenizer = ElectraTokenizer.from_pretrained(model_name)
model = ElectraForSequenceClassification.from_pretrained(model_name)

analyzer = pipeline(
    "sentiment-analysis",
    tokenizer=tokenizer,
    model=model
)

print(analyzer(stt.text))