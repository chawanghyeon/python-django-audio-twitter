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
        self.whisper_model: Any = whisper.load_model("small", device="cpu")
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
        self.gpu_count: int = 0

    def transcribe(self, audio_path: str) -> str:
        result: Any = self.whisper_model.transcribe(audio_path, fp16=False)
        return result["text"]

    def analyze_sentiment(self, text: str) -> str:
        if self.analyzer(text)[0]["label"] == "positive":
            return "긍정"
        else:
            return "부정"

    def check_can_run(self) -> None:
        while True:
            if self.gpu_count >= 8:
                continue
            return

    def get_nouns(self, text) -> List[str]:
        nouns: list[str] = [x for x in self.okt.nouns(text) if len(x) > 1]
        nouns = Counter(nouns).most_common(6)
        return [x[0] for x in nouns]

    def get_keywords(self, audio_path: str) -> List[str]:
        self.check_can_run()

        self.gpu_count += 1
        text: str = self.transcribe(audio_path)
        keywords: List[str] = [self.analyze_sentiment(text)]
        self.gpu_count -= 1

        keywords += self.get_nouns(text)

        return keywords
