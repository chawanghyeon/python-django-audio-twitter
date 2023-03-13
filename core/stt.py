# -*- coding: utf-8 -*-
from collections import Counter
from typing import List

import whisper
from konlpy.tag import Okt
from transformers import ElectraForSequenceClassification, ElectraTokenizer, pipeline


class STT:
    def __init__(self) -> None:
        self.whisper_model = whisper.load_model("small", device="cpu")
        self.tokenizer = ElectraTokenizer.from_pretrained(
            "monologg/koelectra-base-finetuned-nsmc"
        )
        self.electra_model = ElectraForSequenceClassification.from_pretrained(
            "monologg/koelectra-base-finetuned-nsmc"
        )
        self.analyzer = pipeline(
            "sentiment-analysis", tokenizer=self.tokenizer, model=self.electra_model
        )
        self.okt = Okt()
        self.gpu_count = 0

    def transcribe(self, audio_path: str) -> str:
        result = self.whisper_model.transcribe(audio_path, fp16=False)
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
        nouns = [x for x in self.okt.nouns(text) if len(x) > 1]
        nouns = Counter(nouns).most_common(6)
        return [x[0] for x in nouns]

    def get_keywords(self, audio_path: str) -> List[str]:
        self.check_can_run()

        self.gpu_count += 1
        text = self.transcribe(audio_path)
        keywords = [self.analyze_sentiment(text)]
        self.gpu_count -= 1

        keywords += self.get_nouns(text)

        return keywords
