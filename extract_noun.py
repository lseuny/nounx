#-*- coding: utf-8 -*-

import sys
import nounx


if __name__ == '__main__':
    print 'USAGE: python %s DIC_PATH < TEXT_PATH' % (sys.argv[0])

    dic_path = sys.argv[1]

    dic = nounx.load_dic(dic_path)
    postfix_list = nounx.load_postfix()
    postfix_ptn = nounx.make_postfix_ptn(postfix_list)

    for line in sys.stdin:
        print line, # print original sentences
        print '\t',
        n_lst = nounx.extract_noun(line, dic, postfix_ptn)
        for s in n_lst:
            w = s.strip()
            if len(w) < 3: continue
            print '%s' % w,
        print


'''
s = '나는 일본에 여행을 가서 식당에서 식당 음식을 먹었다'

n = nounx.extract_noun(s, dic)
for i in n:
	print i
'''
