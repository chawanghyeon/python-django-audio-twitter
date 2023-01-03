# -*- coding: utf-8 -*-
from transformers import ElectraTokenizer, ElectraForSequenceClassification, pipeline
import whisper
from collections import deque, Counter

# whisper_model = whisper.load_model("large", device="cuda")

# model_name = "monologg/koelectra-base-finetuned-nsmc"
# tokenizer = ElectraTokenizer.from_pretrained(model_name)
# electra_model = ElectraForSequenceClassification.from_pretrained(model_name)

# analyzer = pipeline(
#     "sentiment-analysis",
#     tokenizer=tokenizer,
#     model=electra_model
# )

# stt = whisper_model.transcribe('test.mp3')
# print(analyzer(stt['text']))
# texts = stt['text']
# print(texts)

from krwordrank.sentence import summarize_with_sentences

# keywords = summarize_with_keywords(texts, min_count=5, max_length=10,
#     beta=0.85, max_iter=10, stopwords=stopwords, verbose=True)
texts = '생각이 많은 건 말이야 당연히 해야 할 일이야 나에겐 우리가 지금일 순이야 안전한 유리병을 핑계로 바람을 가둬둔 것 같지만 기억나 그 날에 우리가 잡았던 그 손엔 말이야 설레임보다 커다란 믿음이 담겨서 난 한 바퀴 숨을 졌지만 울음이 날 것도 같아서 소중한 건 언제나 두려움이니까 문을 열면 들리던 목소리 너로 인해 변해 있던 따뜻한 공기 여전히 자신 없지만 은명 저기 사라진 별의 자리 아스라이 하얀빛 한동안은 꺼내 볼 수 있을 거야 합김 없이 반짝인 시간은 조금씩 깨터져 가더라도 너는 맘에 사로잡힐 테니 여긴 서로의 끝이 아닌 새로운 길 모두의 이득감에 진심을 속이지 말자 하나 둘 추억이 떠오르면 많이 많이 그리워할 거야 고맙어요 그래도 이제는 사건의 지평선 너머로 솔직히 두렵기도 하지만 노력은 우리에게 정답이 아니라서 마지막 선물은 산뜻한 우리의 마지막을 기다려줘 우리의 마지막을 기다려줘 이 낭만조각을 보며 잔잔한 스모 מע슬처럼 끝을 퍼줬으면 좋겠어 조금 이따가 단 한 Dream 한국인이 지금 여긴 서로의 끝이 아닌 새로운 길 모두의 익숙함에 진심을 속이지 말자 하나 둘 추억이 떠오르면 많이 많이 그리워할 거야 고맙어요 그래도 이제는 사건의 지평선 너머로 저기 사라진 별의 자리 아슬아슬 이 하얀 빛 한동안은 꺼내볼 수 있을 거야 아낌없이 반짝인 시간은 조금씩 흩어져 가더라도 너와 내 맘에 살아 숨 쉴 테니 여긴 서로의 끝이 아닌 새로운 길 모두의 익숙함에 진심을 속이지 말자 하나 둘 추억이 떠오르면 많이 많이 그리워할 거야 고맙어요 그래도 이제는 사건의 지평선 너머로 사건의 지평선 너머로'
# keywords = summarize_with_sentences(texts, word_count=6)
# print(keywords)
print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
key = Counter(texts.split(" ")).most_common(6)
keyword = []
for i in range(len(key)):
    keyword.append(key[i][0])
print(keyword)


# queuue = deque([])

# while True:
#     if len(queuue) == 0:
#         continue
#     task = queuue.popleft()
#     stt = whisper_model.transcribe(task)
#     analyzer(stt.text)


