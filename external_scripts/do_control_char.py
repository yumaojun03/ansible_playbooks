#!/usr/bin/env python
# coding: utf-8

import re

f = open('input.log', 'rb')
lines =  f.readlines()



bs_chars_re = re.compile(r'(\x08)+')


def bs(line):
    bs_num = []
    delete_num = []
    for match in bs_chars_re.finditer(line):
        s = match.start()
        e = match.end()
        bs_num.append((s,e))
    for num in bs_num:
        delete_num.extend(range(num[0])[:-(num[1]-num[0]+1):-1])
        delete_num.extend([i for i in range(num[1])][num[0]:num[1]])

    l_line = tuple([i for i in line])
    res_num = [i for i in range(len(l_line)) if i not in delete_num]
    res_str = [l_line[i] for i in res_num]
    return ''.join(res_str)


for i in lines:
    print bs(i),




