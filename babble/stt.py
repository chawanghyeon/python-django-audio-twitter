# -*- coding: utf-8 -*-
from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
from collections import deque, Counter
from konlpy.tag import Okt
import whisper

class STT:
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

# text = '생각이 많은 것 말이야 당연히 해야 할 일이야 나에겐 우리가 지금일 순이야 안전한 유리병을 핑계로 바람을 가둬는 것 같지만 기억나 그 날에 우리가 잡았던 그 손엔 말이야 레인보다 커다란 믿음이 담겨서 난 한 바구 숨을 줬지만 울음이 날 것 똑같아서 소중한 건 언제나 두려움이니까 문을 열면 들리던 목소리 어루인 해변에 있던 따뜻한 이 여전히 자신 없지만은 영이 저기 사라진 며느들이 아스라이 라인빛 한다고 하는 건 알고 있을 거야 갚게못이 반짝인 시간은 조금씩 겪어져 가라도 너와는 마음에 사랑 없을 테니 여긴 서로의 끝이 아닌 새로운 게 못은 게 익숙한의 진심을 속이지 말자 하나둘 추억에 떠오르면 많이 많이 그리워할 거야 꿈을 써 그 해도 이제는 사건의 집편선 너머로 그리고ervices 솔직히 두렵기도 하지만 노력은 우리에게 전달이 아니라서 마지막 선물은 산다다 안녕 저기 사라진 멸의 자리 아스라이 하얀 빛 한 덩하는 건을 볼 수 있을 거야 다퀴로 없이 반짝인 시간은 조금씩 깎아져 가라ど 넌은 맘에 사는 아슴 쉴 테니 여긴 서로의 끝이 아닌 새로운 게 목둥이 익숙함의 진심을 속이지 말자 하나둘 추억이 떠오르면 많이 많이 그리워할 거야 그는 굳어서 그래도 이제는 사건의 집 평선 너머로 저기 사라진 멸의 자리 아스라이 하얀 빛 한 덩하는 건을 볼 수 있을 거야 다퀴로 없이 반짝인 시간은 조금씩 깎아져 가라 도 넌은 맘에 사는 아슴 쉴 테니 여긴 서로의 끝이 아닌 새로운 게 목둥이 익숙함의 진심을 속이지 말자 하나둘 추억이 떠오르면 많이 많이 그리워할 거야 그는 굳어서 그래도 이제는 사건의 집 평선 너머로 사건의 집 평선 너머로'