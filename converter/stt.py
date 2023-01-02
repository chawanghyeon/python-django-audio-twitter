from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
import whisper
from collections import deque

whisper_model = whisper.load_model("small", device="cpu")

model_name = "monologg/koelectra-base-finetuned-nsmc"
tokenizer = ElectraTokenizer.from_pretrained(model_name)
electra_model = ElectraForSequenceClassification.from_pretrained(model_name)

analyzer = pipeline(
    "sentiment-analysis",
    tokenizer=tokenizer,
    model=electra_model
)

queuue = deque([])

while True:
    if len(queuue) == 0:
        continue
    task = queuue.popleft()
    stt = whisper_model.transcribe(task)
    analyzer(stt.text)


