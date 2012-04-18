#!/usr/bin/env python
'''Prints the name of the tiers of the specified textgrids. If a
directory is specified, all tier names of teh .TextGrid files in
this directory are printed.'''

import os
import sys
import tgt

EXTENSION = 'TextGrid'

def print_tiernames(filenames):
	for filename in filenames:
		print(filename)
		try:
			tg = tgt.read_textgrid(filename)
			for tiername in tg.get_tier_names():
				print('\t' + tiername)
		except:
			raise Exception(filename + ' caused a problem.')


def main(argv=None):
	if argv is None:
		argv = sys.argv
	if len(argv) < 2:
		print('USAGE: ' + argv[0] + ' <list of TextGrid files or directories>')
	list_of_tg_files = []
	for arg in argv[1:]:
		if os.path.exists(arg):
			if os.path.isdir(arg):
				list_of_tg_files += filter(lambda x: x.endswith(EXTENSION), os.listdir(arg))
			else:
				list_of_tg_files.append(arg)
		else:
			raise FileNotFoundException(arg)
	print_tiernames(list_of_tg_files)

if __name__ == '__main__':
    sys.exit(main())
