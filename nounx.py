#coding: utf8;

import sys, os
import re
import math


# Minimum occurrence of DF(Document Frequency) of words to be a noun candidate.
MIN_DF = 30

ws_ptn = re.compile(u'[^a-zA-Z0-9_ㄱ-ㅎ가-힣]+')
#digit_ptn = re.compile(u'[\d]+')


class NounX:
    def __init__(self, dic_path='dic.txt', postfix_path='postfix.txt'):
        self._dic         = None
        self._phrase      = None
        self._postfix_ptn = None

        dic    = {}
        phrase = {}
        if os.path.isfile(dic_path):
            f = open(dic_path, 'rt')
            for line in f:
                lst = line.strip().split('\t')
                if len(lst) != 2:
                    continue
                try:
                    noun     = lst[0].decode('utf8', 'ignore')
                    noun_lst = noun.split(u' ')
                    if len(noun_lst) == 2:
                        phrase[noun_lst[0]] = noun_lst[1]
                    else:
                        dic[noun] = float(lst[1])
                except:
                    continue
            f.close()
        self._dic    = dic
        self._phrase = phrase

        postfix = []
        f = open(postfix_path, 'rt')
        for line in f:
            if len(line.strip()) < 1:
                continue
            postfix.append(line.strip())
        f.close()

        postfix_re = u'(%s' % postfix[0].decode('utf8', 'ignore')
        for s in postfix[1:]:
            postfix_re += u'|%s' % s.decode('utf', 'ignore')
        postfix_re += u')$'
        self._postfix_ptn = re.compile(postfix_re)


    def extract_noun(self, ustr):
        result    = []
        last_word = ''
        for word in map(lambda x: x.strip(), ws_ptn.split(ustr.lower())):
            if word.endswith(u'들'):
                word = word[:-1]
            if last_word in self._phrase and word in self._phrase[last_word]:
                result.pop()
                result.append('%s%s' % (last_word, word))
                last_word = ''
                continue
            if self._dic.get(word, 0.0) > 0.001:
                result.append(word)
                last_word = word
                continue
            m = self._postfix_ptn.search(word)
            if m == None or m.start() < 2:
                continue
            word = word[:m.start()]
            if word.endswith(u'들'):
                word = word[:-1]
            if last_word in self._phrase and word in self._phrase[last_word]:
                result.pop()
                result.append('%s%s' % (last_word, word))
                last_word = ''
                continue
            if self._dic.get(word, 0.0) > 0.001:
                result.append(word)
                last_word = word
                #continue
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
                m = self._postfix_ptn.search(token)
                if m == None or m.start() < 1:
                    continue
                term    = token[:m.start()]
                postfix = token[m.start():]
                #m = digit_ptn.search(word)
                #if m != None and m.start() >= 0: continue
                if term.endswith(u'들'):
                    term = term[:-1]

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
                p = (0.0 + freq) / s
                if p > 0.0:
                    e -= (p * math.log(p))
            term_entropy[term] = e
        return term_entropy


def main():
    ENTROPY_THRESHOLD = 1.0

    if len(sys.argv) < 2:
        print 'USAGE: python %s TEXT_PATH' % (sys.argv[0])
        return

    text_path = sys.argv[1]

    noun_extractor = NounX()

    term_entropy = noun_extractor.find_new_noun(text_path)

    for term, entropy in term_entropy.items():
        if entropy > ENTROPY_THRESHOLD:
            print '%s\t%.3f' % (term.encode('utf8', 'ignore'), entropy)


if __name__ == '__main__':
    main()

