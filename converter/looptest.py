# import asyncio

# async def main():
#     while True:
#         print("11111")
#         await asyncio.sleep(1)
#         return 33333

# async def main2():
#     while True:
#         print("22222")
#         await asyncio.sleep(1)

# result = 0

# result = asyncio.run(main())
# print(result)

# -*- coding: utf-8 -*-
from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
from collections import deque, Counter
from konlpy.tag import Okt
import whisper

class STT():
    def __init__(self):
        self.whisper_model = whisper.load_model("large", device="cuda")
        self.tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-finetuned-nsmc")
        self.electra_model = ElectraForSequenceClassification.from_pretrained("monologg/koelectra-base-finetuned-nsmc")
        self.analyzer = pipeline("sentiment-analysis", tokenizer=self.tokenizer, model=self.electra_model)
        self.okt = Okt()
        self.queue = deque([])

    def run(self):
        while True:
            if len(self.queue) == 0:
                continue
            audio_path, serializer = self.queue.popleft()
            stt = self.transcribe(audio_path)
            serializer.data['tags'] = self.get_keywords(stt)

    def add(self, audio_path, serializer):
        self.queue.append((audio_path, serializer))

    def transcribe(self, audio_path):
        stt = self.whisper_model.transcribe(audio_path)
        return self.analyzer(stt['text'])

    def get_keywords(self, text):
        nouns = self.okt.nouns(text)
        keywords = [x for x in nouns if len(x) > 1]
        return Counter(self.okt.nouns(keywords)).most_common(5)

import time

stt = STT()

start = time.time()
for _ in range(1):
    text = stt.transcribe("test.mp3")
    stt.get_keywords(text)
print(time.time() - start)