#coding: utf8;

import nounx


noun_extractor = nounx.NounX()

sentence = [ \
    u'우리는 지난 여름에 영국을 여행하는 동안 축구 경기장에서 레알 마드리드의 경기를 참관했다.', \
    u'발견이라는 것은 이해하기도 설명하기도 어렵다.', \
    u'후식을 별로 좋아하지 않아요.', \
    u'오늘은 하루종일 너무 바뻐서 전화할 겨를도 없었다.', \
    u'예쁜 옷을 입고 자동차 차고에서 축구공을 차고 놀았다.', \
    u'나는 나의 눈과 귀조차도 믿을 수가 없었다!', \
    u'심사위원으로는 세계 각국의 유명한 뮤지션들이 초청되었습니다', \
    u'전체적으로 화려함이 돋보이는 곡으로도 유명하다.', \
    u'강요받은 채로 이용당하는 적당한 삶에 만족하지 않겠다!', \
    u'[경북/구미] 결혼기념일 맞이 스테이크가 맛있는 원평동 와인바 <마고>', \
    u'뿌리 깊은 나무는 강한 바람에도 흔들리지 않는다.'
]

for s in sentence:
    print s.encode('utf8', 'ignore')
    print '\t',
    for n in noun_extractor.extract_noun(s):
        print n.encode('utf8', 'ignore'),
    print
    print


