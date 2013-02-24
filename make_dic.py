#-*- coding: utf-8 -*-

import sys
import nounx


# Postfix file path
POSTFIX_PATH = './postfix.txt'

# Entropy Threshold
ENTROPY_THRESHOLD = 0.7


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: python %s TEXT_PATH' % (sys.argv[0])

    text_path = sys.argv[1]

    postfix_list = nounx.load_postfix(POSTFIX_PATH)

    noun_entropy = nounx.compute_noun_entropy(text_path, postfix_list)

    for noun, entropy in noun_entropy.items():
        if entropy > ENTROPY_THRESHOLD:
            print '%s\t%.3f' % (noun, entropy)

