# -*- coding: utf-8 -*-
from ast import keyword
from collections import Counter, deque
from typing import Any, List

import whisper
from konlpy.tag import Okt
from transformers import ElectraForSequenceClassification, ElectraTokenizer, pipeline
from transformers.pipelines import Pipeline


class STT:
    def __init__(self) -> None:
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
        self.running_count: int = 0

    def transcribe(self, audio_path: str) -> str:
        stt: Any = self.whisper_model.transcribe(audio_path)
        return self.analyzer(stt["text"])

    def analyze_sentiment(self, text: str) -> str:
        return self.analyzer(text)[0]["label"]

    def get_keywords(self, audio_path: str) -> List[str]:
        while True:
            if self.running_count >= 8:
                continue
            break
        self.running_count += 1
        text: str = self.transcribe(audio_path)
        keywords: List[str] = [self.analyze_sentiment(text)]
        self.running_count -= 1
        nouns: list[str] = self.okt.nouns(text)
        nouns = [x for x in nouns if len(x) > 1]
        keywords += Counter(self.okt.nouns(nouns)).most_common(6)
        return keywords
