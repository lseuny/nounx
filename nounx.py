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
        self._dic          = None
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
                break
        return result


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
    s = u'발견이라는 것은 이해하기 어렵고 설명하기도 어렵다.'
    print s.encode('utf8', 'ignore')
    print '\t',
    for n in noun_extractor.extract_noun(s):
        print n.encode('utf8', 'ignore'),
    print
    print

    s = u'문창극 총리 후보자'
    print s.encode('utf8', 'ignore')
    print '\t',
    for n in noun_extractor.extract_noun(s):
        print n.encode('utf8', 'ignore'),
    print
    print

    s = u'언론 손석희 앵커'
    print s.encode('utf8', 'ignore')
    print '\t',
    for n in noun_extractor.extract_noun(s):
        print n.encode('utf8', 'ignore'),
    print
    print'''
    
    
    '''testset = [u'축구', u'사람들', u'사람에게도', u'누들', u'해안도로', u'소치스캔들']
    for s in testset:
        print s.encode('utf8', 'ignore')
        print '\t',
        term_list, postfix_list = noun_extractor.find_possible(s)
        for i in term_list:
            print i.encode('utf8', 'ignore'),
        print'''

    ENTROPY_THRESHOLD = 1.0

    if len(sys.argv) < 2:
        print 'USAGE: python %s TEXT_PATH' % (sys.argv[0])
        return

    text_path = sys.argv[1]

    term_entropy = noun_extractor.find_new_noun(text_path)

    for term, entropy in term_entropy.items():
        if entropy > ENTROPY_THRESHOLD:
            print '%s\t%.3f' % (term.encode('utf8', 'ignore'), entropy)


if __name__ == '__main__':
    main()

