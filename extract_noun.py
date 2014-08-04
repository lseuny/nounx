#coding: utf8;

import nounx
import sys
import re

sentence_ptn = re.compile(u'[.?!] ')


if __name__ == '__main__':
    #print 'USAGE: python %s DIC_PATH < TEXT_PATH' % (sys.argv[0])

	noun_extractor = nounx.NounX()

	sentence = [ \
		u'우리는 지난 여름에 영국을 여행하는 동안 축구 경기장에서 레알 마드리드의 경기를 보았다.', \
		u'발견이라는 것은 이해하기도 설명하기도 어렵다.', \
		u'문창극 총리 후보자의 청문회', \
		u'뿌리 깊은 나무는 강한 바람에도 흔들리지 않는다.' \
	]

	for s in sentence:
		print s.encode('utf8', 'ignore')
		print '\t',
		for n in noun_extractor.extract_noun(s):
			print n.encode('utf8', 'ignore'),
		print
		print

	'''
	s = u'우리는 지난 여름에 영국을 여행하는 동안 축구 경기장에서 레알 마드리드의 경기를 보았다.'
	print s.encode('utf8', 'ignore')
	print '\t',
	for n in noun_extractor.extract_noun(s):
		print n.encode('utf8', 'ignore'),
	print
	print

	s = u'발견이라는 것은 이해하기도 설명하기도 어렵다.'
	print s.encode('utf8', 'ignore')
	print '\t',
	for n in noun_extractor.extract_noun(s):
		print n.encode('utf8', 'ignore'),
	print
	print
	'''


	'''
	f = open('sample.txt')
	for line in f:
		ustr = line.decode('utf8', 'ignore')
		for s in sentence_ptn.split(ustr):
			print s.strip().encode('utf8', 'ignore')
			print '\t',
			for n in noun_extractor.extract_noun(s):
				print n.encode('utf8', 'ignore'),
			print
	f.close()
	'''
