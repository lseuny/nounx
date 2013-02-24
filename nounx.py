#-*- coding: utf-8 -*-

import sys
import re
import math


# Minimum DF(Document Frequency) for noun candidates
MIN_DF = 6


ws_ptn = re.compile(u'[\s"]+')


def load_dic(path='./dic.txt'):
    dic = {}
    f = open(path, 'rt')
    for line in f:
        lst = line.strip().split('\t')
        if len(lst) != 2: continue
        if float(lst[1]) < 0: continue
        dic[lst[0]] = lst[1] ### if duplicated??
    f.close()
    return dic


def load_postfix(path='./postfix.txt'):
    postfix = []
    f = open(path, 'rt')
    for line in f:
        if len(line.strip()) < 1: continue
        postfix.append(line.strip())
    f.close()
    return postfix


#def make_postfix_ptn(path='/Users/SL/Projects/lib/dic_postfix.txt'):
def make_postfix_ptn(postfix_list):
    postfix_re = u'(%s' % postfix_list[0].decode('utf8', 'ignore')
    for s in postfix_list:
        postfix_re += u'|%s' % s.decode('utf', 'ignore')
    postfix_re += u')$'
    return re.compile(postfix_re)


def extract_noun(text, dic_noun, postfix_ptn):
    noun_list = []
    ws_ptn = re.compile(u'[\s]+')
    u_text = ws_ptn.sub(u' ', text.lower().decode('utf8', 'ignore'))
    for word in u_text.split(u' '):
        noun = word.encode('utf8', 'ignore')
        if noun in dic_noun:
            noun_list.append(noun)
            continue

        m = postfix_ptn.search(word)
        if m == None or m.start() < 2: continue
        noun = word[:m.start()].encode('utf8', 'ignore')
        if noun in dic_noun:
            noun_list.append(noun)
    return noun_list


def get_noun_candidate(filepath, postfix_list, min_df=MIN_DF):
    postfix_ptn = make_postfix_ptn(postfix_list)

    noun_freq = {}
    f = open(filepath, 'rt')
    for line in f:
        u_str = ws_ptn.sub(u' ', line.lower().decode('utf8', 'ignore'))
        for word in u_str.split(u' '):
            m = postfix_ptn.search(word)
            if m == None or m.start() < 1: continue
            noun = word[:m.start()].encode('utf8', 'ignore')
            if noun not in noun_freq:
                noun_freq[noun]  = 1
            else:
                noun_freq[noun] += 1
    f.close()

    noun_list = []
    for n, f in noun_freq.items():
        if f < min_df: continue
        noun_list.append(n)
    return noun_list


def get_noun_postfix_dist(filepath, noun_list, postfix_list):
    postfix_ptn = make_postfix_ptn(postfix_list)

    noun_postfix = {}

    f = open(filepath, 'rt')
    for line in f:
        u_str = ws_ptn.sub(u' ', line.lower().decode('utf8', 'ignore'))
        for word in u_str.split(u' '):
            m = postfix_ptn.search(word)
            if m == None or m.start() < 2: continue
            noun = word[:m.start()].encode('utf8', 'ignore')
            postfix = word[m.start():].encode('utf8', 'ignore')
            if noun not in noun_list: continue
            if postfix not in postfix_list:
                print '\t\t\t%s' % postfix
                continue
            if noun not in noun_postfix:
                noun_postfix[noun] = [0] * len(postfix_list)
            noun_postfix[noun][postfix_list.index(postfix)] += 1
    f.close()
    
    return noun_postfix


def get_noun_entropy(noun_postfix_dist, postfix_list):
    noun_entropy = {}

    for noun, postfix_freq in noun_postfix_dist.items():
        s = sum(postfix_freq)
        e = 0.0
        p = [0.0] * len(postfix_list)
        for i in range(len(postfix_list)):
            p = postfix_freq[i] * 1.0 / s
            if p > 0.0:
                e -= (p * math.log(p))
        noun_entropy[noun] = e

    return noun_entropy


def compute_noun_entropy(text_path, postfix_list, min_DF=MIN_DF):
    candidates = get_noun_candidate(text_path, postfix_list, min_df)

    noun_postfix_dist = get_noun_postfix_dist(text_path, candidates, postfix_list)

    return get_noun_entropy(noun_postfix_dist, postfix_list)

