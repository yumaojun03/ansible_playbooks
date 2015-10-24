#!/bin/env python


def remove_control_char(filename):
	import re

	file_line_list=open(filename).readlines()

	control_char=re.compile(r"""
				\x1b[ #%()*+\-.\/]. |
				\r |
				(?:\x1b\[|\x9b) [ -?]* [@-~] |
				(?:\x1b\]|\x9d) .*? (?:\x1b\\|[\a\x9c]) |
				(?:\x1b[P^_]|[\x90\x9e\x9f]) .*? (?:\x1b\\|\x9c) |
				\x1b. |
				[\x80-\x9f] |
							""",re.X)
	backspace=re.compile(r"[^\b][\b]")

	for line in file_line_list:
		line_filtered=control_char.sub('',line.rstrip())

		while backspace.search(line_filtered): 	
			line_filtered=backspace.sub('',line_filtered)

		print line_filtered

			


if __name__ == '__main__':
	import sys
	remove_control_char(sys.argv[1])
	
