# from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
# import torch


# device = torch.device("cuda")
# model = ElectraForSequenceClassification.from_pretrained("monologg/koelectra-base-v3-discriminator").to("cuda")
# tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")

# nlp = pipeline("text-classification", model=model, tokenizer=tokenizer)


# print(nlp("이 영화는 정말 재미없었다."))
# print(nlp("이 영화는 정말 재미있었다."))


import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# model_name = "jason9693/koelectra-base-v3-discriminator-apeach"
# model_name = "monologg/koelectra-base-v3-discriminator"
model_name = "skt/kogpt2-base-v2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# set device
# device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
# print("device:", device)
# model.to(device)

nlp = pipeline("text-classification", model=model, tokenizer=tokenizer)
print(nlp("이 영화는 정말 재미없었다."))
print(nlp("이 영화는 정말 재미있었다."))

# from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
# import torch

# tokenizer = AutoTokenizer.from_pretrained("skt/kogpt2-base-v2")
# model = AutoModelForSequenceClassification.from_pretrained("skt/kogpt2-base-v2")
# device = torch.device("cuda")
# model.to(device)
# pipe = pipeline("text-classification", model=model, tokenizer=tokenizer)

# print(pipe("이 영화는 정말 재미없었다."))