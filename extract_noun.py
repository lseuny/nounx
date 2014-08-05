#coding: utf8;

import nounx
import sys
import re

sentence_ptn = re.compile(u'[.?!] ')


if __name__ == '__main__':
	noun_extractor = nounx.NounX()

	sentence = [ \
		u'우리는 지난 여름에 영국을 여행하는 동안 축구 경기장에서 레알 마드리드의 경기를 참관했다.', \
		u'발견이라는 것은 이해하기도 설명하기도 어렵다.', \
		u'오늘은 하루종일 너무 바뻐서 전화할 겨를도 없었다.', \
		u'문창극 총리 후보자의 청문회', \
		u'나는 나의 눈과 귀조차도 믿을 수가 없었다!', \
		u'심사위원으로는 세계 각국의 유명한 뮤지션들이 초청되었습니다', \
		u'뿌리 깊은 나무는 강한 바람에도 흔들리지 않는다.' \
	]

	for s in sentence:
		print s.encode('utf8', 'ignore')
		print '\t',
		for n in noun_extractor.extract_noun(s):
			print n.encode('utf8', 'ignore'),
		print
		print

