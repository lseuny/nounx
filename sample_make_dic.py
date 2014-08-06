#coding: utf8;

import nounx
import sys

ENTROPY_THRESHOLD = 1.0


# 사전을 만든다.

if len(sys.argv) < 2:
    print 'USAGE: python %s TEXT_PATH' % (sys.argv[0])
    exit(-1)

text_path = sys.argv[1]

noun_extractor = nounx.NounX()

term_entropy = noun_extractor.find_new_noun(text_path)

for term, entropy in term_entropy.items():
    if entropy > ENTROPY_THRESHOLD:
        print '%s\t%.3f' % (term.encode('utf8', 'ignore'), entropy)

