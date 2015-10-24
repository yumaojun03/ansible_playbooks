#!/bin/env python
# coding: utf-8


def remove_control_char(filename):
	import re

	file_line_list=open(filename).readlines()

	control_char=re.compile(r"""
				\x1b[ #%()*+\-.\/]. |
				\r |                                               #匹配 回车符(CR) 
				(?:\x1b\[|\x9b) [ -?]* [@-~] |                     #匹配 控制顺序描述符(CSI)... Cmd
				(?:\x1b\]|\x9d) .*? (?:\x1b\\|[\a\x9c]) |          #匹配 操作系统指令(OSC)...终止符或振铃符(ST|BEL)
				(?:\x1b[P^_]|[\x90\x9e\x9f]) .*? (?:\x1b\\|\x9c) | #匹配 设备控制串或私讯或应用程序命令(DCS|PM|APC)...终止符(ST)
				\x1b. |                                            #匹配 转义过后的字符
				[\x80-\x9f] |                                      #匹配 所有控制字符 
				""",
                                re.X)
	backspace=re.compile(r"[^\b][\b]")

	for line in file_line_list:
		line_filtered=control_char.sub('',line.rstrip())

		while backspace.search(line_filtered): 	
			line_filtered=backspace.sub('',line_filtered)

		print line_filtered

			


if __name__ == '__main__':
	import sys
	remove_control_char(sys.argv[1])
	
