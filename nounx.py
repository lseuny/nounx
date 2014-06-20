#-*- coding: utf-8 -*-

import sys
import re
import math


# Minimum occurrence of DF(Document Frequency) of words to be a noun candidate
MIN_DF = 30


#ws_ptn = re.compile(u'[\s"''.,;:/!?@()[\]]+')
ws_ptn = re.compile(u'[^a-zA-Z0-9_ㄱ-ㅎ가-힣]+')


def load_dic(path='./dic.txt'):
    dic = {}
    f = open(path, 'rt')
    for line in f:
        lst = line.strip().split('\t')
        if len(lst) != 2: continue
        #if float(lst[1]) < 0: continue
        dic[lst[0]] = float(lst[1]) ### if duplicated??
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
    u_text = ws_ptn.sub(u' ', text.lower().decode('utf8', 'ignore'))
    for word in u_text.split(u' '):
        if word.endswith(u'들'):
            word = word[:-1]
        noun = word.encode('utf8', 'ignore')
        if noun in dic_noun and dic_noun[noun] > 0.1:
            noun_list.append(noun)
            continue

        m = postfix_ptn.search(word)
        if m == None or m.start() < 2: continue
        word = word[:m.start()]
        if word.endswith(u'들'):
            word = word[:-1]
        elif word.endswith(u'에서'):
            word = word[:-2]
        noun = word.encode('utf8', 'ignore')
        if noun in dic_noun and dic_noun[noun] > 0.1:
            noun_list.append(noun)
    return noun_list


def get_noun_candidate(filepath, postfix_list, min_df=MIN_DF):
    postfix_ptn = make_postfix_ptn(postfix_list)
    digit_ptn = re.compile(u'[0-9]+')

    noun_df = {}
    f = open(filepath, 'rt')
    for line in f:
        u_str = ws_ptn.sub(u' ', line.lower().decode('utf8', 'ignore'))
        noun_tf = {}
        for word in u_str.split(u' '):
            m = postfix_ptn.search(word)
            if m == None or m.start() < 1: continue
            word = word[:m.start()]
            m = digit_ptn.search(word)
            if m != None and m.start() >= 0: continue
            if word.endswith(u'들'):
                word = word[:-1]
            elif word.endswith(u'에서'):
                word = word[:-2]
            noun = word.encode('utf8', 'ignore')
            if noun not in noun_tf:
                noun_tf[noun] = 0
            noun_tf[noun] += 1
        for n in noun_tf.keys():
            if n not in noun_df:
                noun_df[n] = 0
            noun_df[n] += 1
    f.close()

    noun_list = []
    for n, df in noun_df.items():
        if df < min_df:
            continue
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
            u_noun = word[:m.start()]
            if u_noun.endswith(u'들'):
                u_noun = u_noun[:-1]
            elif u_noun.endswith(u'에서'):
                u_noun = u_noun[:-2]
            noun = u_noun.encode('utf8', 'ignore')
            postfix = word[m.start():].encode('utf8', 'ignore')
            if noun not in noun_list: continue
            if postfix not in postfix_list: continue
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


def compute_noun_entropy(text_path, postfix_list, min_df=MIN_DF):
    candidates = get_noun_candidate(text_path, postfix_list, min_df)

    noun_postfix_dist = get_noun_postfix_dist(text_path, candidates, postfix_list)

    return get_noun_entropy(noun_postfix_dist, postfix_list)

