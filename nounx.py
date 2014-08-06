#coding: utf8;

import sys, os
import re
import math


# Minimum occurrence of DF(Document Frequency) of words to be a noun candidate.
MIN_DF = 30

ws_ptn    = re.compile(u'[^a-zA-Z0-9_ㄱ-ㅎ가-힣]+')
digit_ptn = re.compile(u'[\d]+')


class NounX:
    def __init__(self, dic_path='dic.txt', postfix_path='postfix.txt'):
        self._dic         = None
        self._postfix_ptn = [None, None]

        dic = {}
        if os.path.isfile(dic_path):
            f = open(dic_path, 'rt')
            for line in f:
                lst = line.strip().decode('utf8', 'ignore').split(u'\t')
                if len(lst) != 2:
                    continue
                try:
                    dic[lst[0]] = float(lst[1])
                except:
                    continue
            f.close()
        self._dic = dic

        postfix = [[], []]
        f = open(postfix_path, 'rt')
        for line in f:
            lst = line.strip().decode('utf8', 'ignore').split(u'\t')
            if len(lst) != 2:
                continue
            priority = int(lst[0]) - 1
            postfix[priority].append(lst[1])
        f.close()

        for i in xrange(2):
            postfix_re = u'(%s' % postfix[i][0]
            for s in postfix[i][1:]:
                postfix_re += u'|%s' % s
            postfix_re += u')$'
            self._postfix_ptn[i] = re.compile(postfix_re)


    def add_candidate(self, token, postfix, depth, term_list, postfix_list):
        assert depth <= 2

        # 특정 조사로 끝나는 명사는 별로 없음을 이용하는 휴리스틱
        if len(token) > 1:
            if token.endswith(u'에'):
                #if token not in [u'누에', u'멍에', u'성에', u'벨기에', u'오보에', u'마로니에', u'샹들리에', u'아틀리에']
                if token[-2] not in [u'누', u'멍', u'성', u'기', u'보', u'니', u'리', u'리']:
                    token   = token[:-1]
                    postfix = u'에' + postfix
            elif token.endswith(u'를'): # "겨를" 외에 또 있나?
                if token[-2] not in [u'겨']:
                    token   = token[:-1]
                    postfix = u'를' + postfix

        if token not in term_list:
            term_list.append(token) # 누들 -> 누들
            postfix_list.append(postfix)

        if token.endswith(u'들'): # 사람들 -> 사람, 누들 -> 누
            if token[:-1] not in term_list:
                term_list.append(token[:-1])
                postfix_list.append(u'들')

        if depth < 2:
            m = self._postfix_ptn[depth].search(token)
            if m != None and m.start() > 0:
                self.add_candidate(token[:m.start()], token[m.start():], depth + 1, term_list, postfix_list)
            elif depth < 1:
                self.add_candidate(token[:], u'', depth + 1, term_list, postfix_list)


    def find_possible(self, token):
        term_list    = []
        postfix_list = []
        self.add_candidate(token, u'', 0, term_list, postfix_list)
        return (term_list, postfix_list)


    def extract_noun(self, ustr, use_phrase=True):
        result = []
        for token in map(lambda x: x.strip(), ws_ptn.split(ustr.lower())):
            candidate_list, postfix_list = self.find_possible(token)
            found = False
            for candidate in candidate_list:
                if self._dic.get(candidate, 0.0) < 0.001:
                    continue
                if use_phrase == True:
                    phrase = candidate
                    while len(result) > 0:
                        phrase_try = u'%s%s' % (result[-1], phrase)
                        if phrase_try not in self._dic:
                            break
                        phrase = phrase_try
                        result.pop()
                    if self._dic.get(phrase, 0.0) > 0.001:
                        result.append(phrase)
                else: # not use phrase
                    result.append(candidate)
                found = True
                break
            if found == False:
                result.append(u'\t') # 알 수 없는 토큰일 때는 탭문자를 넣어서 "A \t B"가 "AB"의 프레이지로 잡히지 않게 한다. 최종 결과를 리턴할 때는 명사 리스트에서 탭문자를 제거해준다.
        return filter(lambda x: x != u'\t', result)


    def find_new_noun(self, text_path, min_df=MIN_DF):
        term_df      = {}
        term_postfix = {}
        term_entropy = {}

        f = open(text_path, 'rt')
        for line in f: # a line is a document
            term_tf = {} # term frequency in a docuemnt
            ustr    = line.decode('utf8', 'ignore').lower()
            for token in map(lambda x: x.strip(), ws_ptn.split(ustr)):
                m = digit_ptn.search(token)
                if m != None and m.start() >= 0:
                    continue

                if token in self._dic:
                    continue

                # "사람에게도" -> ["사람에게도", "사람에게", "사람"]
                # "해안도로" -> ["해안도로", "해안도"]
                term_list, postfix_list = self.find_possible(token)
                for i in xrange(len(term_list)-1, 0, -1):
                    term    = term_list[i]
                    postfix = postfix_list[i]
                    if term in self._dic:
                        break

                    if term not in term_tf:
                        term_tf[term] = 0
                    term_tf[term] += 1

                    if term not in term_postfix:
                        term_postfix[term] = {}
                    if postfix not in term_postfix[term]:
                        term_postfix[term][postfix] = 0
                    term_postfix[term][postfix] += 1

            for term in term_tf.keys():
                if term not in term_df:
                    term_df[term] = 0
                term_df[term] += 1
        f.close()

        for term, df in term_df.items():
            if df < min_df:
                continue
            if term in self._dic:
                continue
            if len(term) < 2:
                continue
            postfix_freq = term_postfix.get(term, {})
            s = sum(postfix_freq.values())
            e = 0.0
            for postfix, freq in postfix_freq.items():
                if freq < 3:
                    continue
                #print '%s\t%d\t%s' % (term.encode('utf8', 'ignore'), freq, postfix.encode('utf8', 'ignore'))
                p = (0.0 + freq) / s
                if p > 0.0:
                    e -= (p * math.log(p))
            term_entropy[term] = e
        return term_entropy


def main():
    noun_extractor = NounX()
    
    '''
    testset = [u'축구', u'사람들', u'사람에게도', u'누들', u'해안도로', u'스캔들', u'바람에도', u'학교에서만은']
    for s in testset:
        print s.encode('utf8', 'ignore')
        print '\t',
        term_list, postfix_list = noun_extractor.find_possible(s)
        for i in term_list:
            print i.encode('utf8', 'ignore'),
        print
    '''

    '''
    sentence = [ \
        u'우리는 지난 여름에 영국을 여행하는 동안 축구 경기장에서 레알 마드리드의 경기를 참관했다.', \
        u'발견이라는 것은 이해하기도 설명하기도 어렵다.', \
        u'오늘은 하루종일 너무 바뻐서 전화할 겨를도 없었다.', \
        u'나는 나의 눈과 귀조차도 믿을 수가 없었다!', \
        u'심사위원으로는 세계 각국의 유명한 뮤지션들이 초청되었습니다', \
        u'전체적으로 화려함이 돋보이는 곡으로도 유명하다.', \
        u'뿌리 깊은 나무는 강한 바람에도 흔들리지 않는다.'
    ]

    for s in sentence:
        print s.encode('utf8', 'ignore')
        print '\t',
        for n in noun_extractor.extract_noun(s):
            print n.encode('utf8', 'ignore'),
        print
        print
    '''


if __name__ == '__main__':
    main()

