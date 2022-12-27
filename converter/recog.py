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