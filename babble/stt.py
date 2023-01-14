# -*- coding: utf-8 -*-
from collections import Counter, deque
from threading import Thread
from typing import Any

import whisper
from konlpy.tag import Okt
from transformers import ElectraForSequenceClassification, ElectraTokenizer, pipeline
from transformers.pipelines import Pipeline


class STT(Thread):
    def __init__(self) -> None:
        super().__init__(daemon=True)
        self.whisper_model: Any = whisper.load_model("large", device="cuda")
        self.tokenizer: Any = ElectraTokenizer.from_pretrained(
            "monologg/koelectra-base-finetuned-nsmc"
        )
        self.electra_model: Any = ElectraForSequenceClassification.from_pretrained(
            "monologg/koelectra-base-finetuned-nsmc"
        )
        self.analyzer: Pipeline = pipeline(
            "sentiment-analysis", tokenizer=self.tokenizer, model=self.electra_model
        )
        self.okt: Okt = Okt()
        self.queue: deque = deque([])

    def run(self) -> None:
        while True:
            if len(self.queue) == 0:
                continue
            audio_path: str
            serializer: Any
            audio_path, serializer = self.queue.popleft()
            stt: str = self.transcribe(audio_path)
            serializer.data["tags"] = self.get_keywords(stt)

    def add(self, audio_path, serializer) -> None:
        self.queue.append((audio_path, serializer))

    def transcribe(self, audio_path) -> str:
        stt: Any = self.whisper_model.transcribe(audio_path)
        return self.analyzer(stt["text"])

    def get_keywords(self, text) -> str:
        nouns: list[str] = self.okt.nouns(text)
        keywords: list[str] = [x for x in nouns if len(x) > 1]
        return Counter(self.okt.nouns(keywords)).most_common(5)
